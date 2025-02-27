import asyncio
import csv
import io
from collections.abc import Awaitable
from pathlib import Path
from typing import Any

import aiofiles  # type: ignore
import typer
from openai import AsyncOpenAI

from .evaluator import evaluate_response_async


async def process_row(
    row: dict[str, Any],
    story_text: str,
    question_text: str,
    rubric_text: str,
    model: str,
    client: AsyncOpenAI,
    scoring_format: str,
    progress: Any,
) -> dict[str, Any]:
    """Asynchronously process a single row, update progress, and return the updated row."""
    response_data = await evaluate_response_async(
        row.get("Student Constructed Response", ""),
        story_text,
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
    story_text: str,
    question_text: str,
    rubric_text: str,
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
            process_row(row, story_text, question_text, rubric_text, model, client, scoring_format, progress)
            for row in rows
        ]
        processed_rows = await asyncio.gather(*tasks)

    async with aiofiles.open(output_file, mode="w", encoding="utf-8-sig", newline="") as outfile:
        await outfile.write(",".join(fieldnames) + "\n")

        for row in processed_rows:
            await outfile.write(
                ",".join(f'"{row[field]}"' if "," in str(row[field]) else str(row[field]) for field in fieldnames)
                + "\n"
            )

    typer.echo(f"\nEvaluation completed. Results saved to {output_file}")


def run_async_process_csv(
    input_file: Path,
    output_file: Path,
    story_text: str,
    question_text: str,
    rubric_text: str,
    model: str,
    client: AsyncOpenAI,
    scoring_format: str,
) -> None:
    """Wrapper function to run the async function from a synchronous context."""
    asyncio.run(
        process_csv(input_file, output_file, story_text, question_text, rubric_text, model, client, scoring_format)
    )
