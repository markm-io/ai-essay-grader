import asyncio
import csv
import io
from collections.abc import Awaitable
from pathlib import Path
from typing import Any

import aiofiles  # type: ignore
import typer
from aiocsv import AsyncDictWriter  # new import for asynchronous CSV writing
from openai import AsyncOpenAI

from .evaluator import evaluate_response_async


async def process_row(
    row: dict[str, Any],
    story_dict: dict[str, Any],
    question_text: str,
    rubric_text: dict[str, Any],
    model: str,
    client: AsyncOpenAI,
    scoring_format: str,
    progress: Any,
) -> dict[str, Any]:
    """Asynchronously process a single row, update progress, and return the updated row."""
    response_data = await evaluate_response_async(
        row.get("Student Constructed Response", ""),
        row.get("Enrolled Grade Level", ""),
        row.get("Tested Language", ""),
        story_dict,
        question_text,
        rubric_text,
        model,
        client,
        scoring_format,
    )
    if response_data:
        row.update(response_data)

    progress.update(1)
    return row


async def process_csv(
    input_file: Path,
    output_file: Path,
    story_dict: dict[str, Any],
    question_text: str,
    rubric_text: dict[str, Any],
    model: str,
    client: AsyncOpenAI,
    scoring_format: str,
) -> None:
    """Process the input CSV file asynchronously, evaluate responses concurrently, and write results asynchronously."""
    async with aiofiles.open(input_file, encoding="utf-8") as infile:
        content = await infile.read()
        content_io = io.StringIO(content)
        reader = csv.DictReader(content_io)

        base_fieldnames = reader.fieldnames if reader.fieldnames else []
        additional_fields = (
            [
                "idea_development_score",
                "idea_development_feedback",
                "language_conventions_score",
                "language_conventions_feedback",
            ]
            if scoring_format == "extended"
            else ["score", "feedback"]
        )
        fieldnames = [*base_fieldnames, *additional_fields]
        rows = list(reader)

    total_rows = len(rows)
    typer.echo("Evaluating responses...")

    with typer.progressbar(length=total_rows, label="Processing responses") as progress:
        tasks: list[Awaitable[dict[str, Any]]] = [
            process_row(row, story_dict, question_text, rubric_text, model, client, scoring_format, progress)
            for row in rows
        ]
        processed_rows = await asyncio.gather(*tasks)

    # Use aiocsv's AsyncDictWriter to write the output CSV asynchronously
    async with aiofiles.open(output_file, mode="w", encoding="utf-8-sig", newline="") as outfile:
        writer = AsyncDictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        await writer.writeheader()
        await writer.writerows(processed_rows)

    typer.echo(f"\nEvaluation completed. Results saved to {output_file}")


def run_async_process_csv(
    input_file: Path,
    output_file: Path,
    story_dict: dict[str, Any],
    question_text: str,
    rubric_text: dict[str, Any],
    model: str,
    client: AsyncOpenAI,
    scoring_format: str,
) -> None:
    """

        Wrapper function to run the async function from a synchronous context.

    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
        story_dict: Dictionary of story text
        question_text: Question text
        rubric_text: Dictionary of rubric text
        model: OpenAI model identifier
        client: OpenAI client instance
        scoring_format: Format for score presentation

    Returns:
        Parsed response score object or None if an error occurs


    """
    print(f"Running process using {model} model")
    asyncio.run(
        process_csv(input_file, output_file, story_dict, question_text, rubric_text, model, client, scoring_format)
    )
