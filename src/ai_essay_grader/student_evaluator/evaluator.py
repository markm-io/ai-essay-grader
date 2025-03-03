import asyncio
import json
import time
from typing import Any, Union

import tiktoken
import typer
from openai import AsyncOpenAI, OpenAIError, RateLimitError

from .models import ExtendedResponseScore, ResponseScore

# OpenAI Token Rate Limits
MAX_TOKENS_PER_MIN = 200_000  # 200,000 tokens per minute
TOKEN_USAGE = 0  # Ensure TOKEN_USAGE is initialized
TOKEN_RESET_TIME = time.time() + 60  # Reset every 60 seconds


async def enforce_rate_limit(estimated_tokens: int) -> int:
    """

        Ensures the API stays under the token limit per minute.

        If the estimated tokens exceed the limit, waits until the next reset.

    Args:
        estimated_tokens: Number of tokens estimated for the current request

    Returns:
        Updated token usage

    """
    global TOKEN_USAGE, TOKEN_RESET_TIME  # Declare global before modifying

    # Reset token usage every minute
    if time.time() > TOKEN_RESET_TIME:
        TOKEN_USAGE = 0
        TOKEN_RESET_TIME = time.time() + 60

    # Wait if exceeding the limit
    while TOKEN_USAGE + estimated_tokens > MAX_TOKENS_PER_MIN:
        wait_time = TOKEN_RESET_TIME - time.time()
        if wait_time > 0:
            # typer.echo(f"Rate limit approaching. Sleeping for {wait_time:.2f} seconds...")
            await asyncio.sleep(wait_time)
        else:
            break

    # Update token usage
    TOKEN_USAGE += estimated_tokens  # Modify global variable
    return TOKEN_USAGE


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
        Returns token count for a given text and model.

    Args:
        text: The text to be tokenized
        model: OpenAI model identifier

    Returns:
        Number of tokens in the encoded text

    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


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
    Asynchronously evaluate a student's response using OpenAI's API with rate limiting and retry logic.

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
    global TOKEN_USAGE  # Declare global before modifying

    if scoring_format == "extended":
        extended_system_content = (
            "four keys: 'idea_development_score' (an integer), 'idea_development_feedback' (a string), "
            "'language_conventions_score' (an integer), and 'language_conventions_feedback' (a string)"
        )
    else:
        extended_system_content = "two keys: 'score' (an integer) and 'feedback' (a string)"

    # Normalize language format
    tested_language = tested_language.strip().lower()

    # Language instructions
    if tested_language == "spanish":
        language_instruction = (
            "El estudiante ha realizado la prueba en español. "
            "Proporcione la retroalimentación y la evaluación en español."
        )
    else:
        language_instruction = "The student has taken the test in English. Provide feedback and evaluation in English."

    # Structured prompt to reduce token usage
    user_prompt = {
        "grade_level": f"Grade {grade_level}",
        "language": tested_language.capitalize(),
        "stories": story_dict,
        "question": question_text,
        "rubric": rubric_text,
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
                f"AI Grader: Evaluate student responses based on rubric. "
                f"Your task is to assess the student's answer using the provided story, question, and rubric. "
                f"Return your evaluation strictly as a JSON object with exactly {extended_system_content}. "
                f"Do not include any additional text or commentary. Ensure that the JSON output is valid and parsable."
            ),
        },
        user_message,
    ]

    response_format = ExtendedResponseScore if scoring_format == "extended" else ResponseScore

    # Estimate token usage before request
    prompt_tokens = count_tokens(json.dumps(user_prompt), model)
    max_completion_tokens = 2000  # Expected output token size

    # Ensure rate limit is not exceeded
    await enforce_rate_limit(prompt_tokens + max_completion_tokens)

    for attempt in range(5):  # Increased retries
        try:
            response = await client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                temperature=0,
                response_format=response_format,
                max_tokens=max_completion_tokens,
            )

            # Extract token usage from response
            completion_tokens = response.usage.completion_tokens
            total_tokens_used = prompt_tokens + completion_tokens

            global TOKEN_USAGE  # Declare again in case it's lost in async
            TOKEN_USAGE += total_tokens_used  # Modify global variable

            # Extract text from response
            response_text = response.choices[0].message.content.strip()

            # Validate JSON format
            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError as e:
                typer.echo(f"JSON parsing error: {e}\nRaw Response: {response_text}", err=True)
                return None

            return parsed_response

        except RateLimitError as e:
            # Extract wait time from OpenAI response
            retry_after = getattr(e, "retry_after", 2)
            # typer.echo(f"Rate limit exceeded. Retrying in {retry_after} seconds...", err=True)
            await asyncio.sleep(retry_after)  # Wait before retrying

        except (OpenAIError, json.JSONDecodeError) as e:
            typer.echo(f"Error during API call or response parsing: {e}", err=True)
            if attempt < 4:
                retry_time = 2**attempt  # Exponential backoff
                typer.echo(f"Retrying in {retry_time} seconds...", err=True)
                await asyncio.sleep(retry_time)
            else:
                return None
    return None
