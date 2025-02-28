from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from .csv_processor import run_async_process_csv


def grade_responses(
    input_file: Path,
    output_file: Path,
    story_text: str,
    question_text: str,
    rubric_text: dict[str, Any],
    ai_model: str,
    client: AsyncOpenAI,
    scoring_format: str,
) -> None:
    """Processes student responses and evaluates them using OpenAI."""
    model_mapping = {
        "extended": "ft:gpt-4o-mini-2024-07-18:securehst::B4sRHMIY",
        "item-specific": "ft:gpt-4o-mini-2024-07-18:securehst::B5c3pEjL",
        "short": "ft:gpt-4o-mini-2024-07-18:securehst::B5c3pEjL",
    }
    model = model_mapping.get(scoring_format, ai_model)

    # process_csv(input_file, output_file, story_text, question_text, rubric_text, model, client, scoring_format)
    run_async_process_csv(
        input_file, output_file, story_text, question_text, rubric_text, model, client, scoring_format
    )
