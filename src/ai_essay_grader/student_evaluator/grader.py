from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from .csv_processor import run_async_process_csv


def grade_responses(
    input_file: Path,
    output_file: Path,
    story_dict: dict[str, Any],
    question_text: str,
    rubric_text: dict[str, Any],
    ai_model: str,
    client: AsyncOpenAI,
    scoring_format: str,
) -> None:
    """Processes student responses and evaluates them using OpenAI."""
    model_mapping = {
        "extended": "ft:gpt-4o-mini-2024-07-18:securehst::B6YDFKyO",
        "item-specific": "ft:gpt-4o-mini-2024-07-18:securehst::B72LJHWZ",
        "short": "ft:gpt-4o-mini-2024-07-18:securehst::B79Kzt5H",
    }
    if ai_model:
        model = ai_model
    else:
        model = model_mapping.get(scoring_format, ai_model)

    run_async_process_csv(
        input_file, output_file, story_dict, question_text, rubric_text, model, client, scoring_format
    )
