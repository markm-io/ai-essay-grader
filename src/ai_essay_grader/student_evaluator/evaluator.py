import json
from typing import Union

import typer
from openai import OpenAI, OpenAIError

from .models import ExtendedResponseScore, ResponseScore


def evaluate_response(
    student_response: str,
    story_text: str,
    question_text: str,
    rubric_text: str,
    model: str,
    client: OpenAI,
    scoring_format: str,
) -> Union[ExtendedResponseScore, ResponseScore, None]:
    """
    Evaluate a student's response using OpenAI's API.

    Args:
        student_response: The student's written response
        story_text: The story text used in the question
        question_text: The question prompt
        rubric_text: The grading rubric
        model: OpenAI model identifier
        client: OpenAI client instance
        scoring_format: Format of scoring output ("extended" or "short")

    Returns:
        Parsed response score object or None if error occurs

    """
    messages = [
        {
            "role": "system",
            "content": "You are an AI trained to evaluate student responses based on a rubric. "
            "Please evaluate the student response based on the story, question, and "
            "rubric provided, and return your response strictly as a JSON object.",
        },
        {
            "role": "user",
            "content": f"Story:\n{story_text}\n\n"
            f"Question:\n{question_text}\n\n"
            f"Rubric:\n{rubric_text}\n\n"
            f"Student Response:\n{student_response}",
        },
    ]

    response_format = ExtendedResponseScore if scoring_format == "extended" else ResponseScore

    try:
        response = client.beta.chat.completions.parse(
            model=model, messages=messages, temperature=0, response_format=response_format
        )
        response_text = response.choices[0].message.content
        return json.loads(response_text)
    except (OpenAIError, json.JSONDecodeError) as e:
        typer.echo(f"Error during API call or response parsing: {e}", err=True)
        return None
