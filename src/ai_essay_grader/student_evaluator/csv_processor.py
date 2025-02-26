import csv
from pathlib import Path

import typer
from openai import OpenAI

from .evaluator import evaluate_response


def process_csv(
    input_file: Path,
    output_file: Path,
    story_text: str,
    question_text: str,
    rubric_text: str,
    model: str,
    client: OpenAI,
    scoring_format: str,
) -> None:
    """Process the input CSV file, evaluate responses, and write results to an output CSV."""
    with input_file.open(mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
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

    with output_file.open(mode="w", newline="", encoding="utf-8-sig") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        with typer.progressbar(rows, length=total_rows, label="Evaluating responses") as progress:
            for row in progress:
                response_data = evaluate_response(
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
                writer.writerow(row)

    typer.echo(f"\nEvaluation completed. Results saved to {output_file}")
