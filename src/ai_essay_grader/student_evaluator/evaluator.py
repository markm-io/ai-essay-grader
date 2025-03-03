import asyncio
import json
from typing import Any, Union

import typer
from openai import AsyncOpenAI, OpenAIError

from .models import ExtendedResponseScore, ResponseScore


async def evaluate_response_async(
    student_response: str,
    grade_level: str,
    tested_language: str,
    story_dict: dict[str, Any],
    question_text: str,
    rubric_text: dict[str, Any],
    model: str,
    client: AsyncOpenAI,
    scoring_format: str,
) -> Union[ExtendedResponseScore, ResponseScore, None]:
    """
    Asynchronously evaluate a student's response using OpenAI's API.

    Args:
        student_response: The student's written response
        grade_level: The grade level of the student
        tested_language: The language being tested
        story_dict: The story text used in the question
        question_text: The question prompt
        rubric_text: The grading rubric
        model: OpenAI model identifier
        client: OpenAI client instance
        scoring_format: Format of scoring output ("extended", "item-specific", or "short")

    Returns:
        Parsed response score object or None if an error occurs

    """
    if scoring_format == "extended":
        extended_system_content = (
            "four keys: 'idea_development_score' (an integer), 'idea_development_feedback' (a string)"
            ", 'language_conventions_score' (an integer), and 'language_conventions_feedback' (a string)"
        )
    else:
        extended_system_content = "two keys: 'score' (an integer) and 'feedback' (a string)"

    # Extract additional context
    tested_language = tested_language.strip().lower()  # Normalize language format

    # Language settings (English or Spanish)
    if tested_language == "spanish":
        language_instruction = (
            "El estudiante ha realizado la prueba en español. "
            "Proporcione la retroalimentación y la evaluación en español."
        )
    else:
        language_instruction = "The student has taken the test in English. Provide feedback and evaluation in English."

    # Structured prompt to reduce token usage and dynamically insert rubric
    user_prompt = {
        "grade_level": f"Grade {grade_level}",
        "language": tested_language.capitalize(),
        "stories": story_dict,  # Dictionary of multiple stories
        "question": question_text,
        "rubric": rubric_text,  # Use structured or flattened rubric
        "student_response": student_response,
        "evaluation_guidance": (
            f"Analyze the student's response in a grade-appropriate manner. "
            f"Ensure feedback aligns with expectations for Grade {grade_level}. "
            f"{language_instruction}"
        ),
    }

    user_message = {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}

    messages = [
        {
            "role": "system",
            "content": (
                f"AI Grader: Evaluate student responses based on rubric."
                f"Your task is to assess the student's answer using the provided story, question, and rubric. "
                f"Return your evaluation strictly as a JSON object with exactly {extended_system_content}. "
                f"Do not include any additional text or commentary. Ensure that the JSON output is valid and parsable."
            ),
        },
        user_message,
    ]

    response_format = ExtendedResponseScore if scoring_format == "extended" else ResponseScore

    for attempt in range(3):
        try:
            response = await client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                temperature=0,
                response_format=response_format,
                stop=["###"],
                max_completion_tokens=2000,
            )

            # Extract text from response
            response_text = response.choices[0].message.content.strip()

            # Validate JSON format
            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError as e:
                typer.echo(f"JSON parsing error: {e}\nRaw Response: {response_text}", err=True)
                return None

            return parsed_response

        except (OpenAIError, json.JSONDecodeError) as e:
            typer.echo(f"Error during API call or response parsing: {e}", err=True)
            if attempt < 2:
                typer.echo("Retrying...", err=True)
                await asyncio.sleep(2)  # Wait for 2 seconds before retrying

    return None
