from pathlib import Path

import typer
from openai import OpenAI

from .file_utils import read_file
from .grader import grade_responses

grader_app = typer.Typer()


@grader_app.command()
def main(
    input_file: Path,
    ai_model: str,
    story_file: Path,
    question_file: Path,
    rubric_file: Path,
    api_key: str,
    output: Path,
    scoring_format: str,
) -> None:
    """
    CLI entry point for grading student responses.

    Args:
        input_file (Path): CSV file containing student responses to be graded
        ai_model (str): Identifier for the OpenAI model to be used
        story_file (Path): Text file containing the story or passage
        question_file (Path): Text file containing the questions
        rubric_file (Path): Text file containing the grading rubric
        api_key (str): OpenAI API authentication key
        output (Path): Destination CSV file for graded responses
        scoring_format (str): Format for score presentation (extended/short)

    """
    input_file = typer.Option(..., help="Path to the input CSV file.") if input_file is None else input_file
    ai_model = (typer.Option(..., help="OpenAI model identifier."),) if ai_model is None else ai_model
    story_file = (typer.Option(..., help="Path to the story text file."),) if story_file is None else story_file
    question_file = (
        (typer.Option(..., help="Path to the question text file."),) if question_file is None else question_file
    )
    rubric_file = (typer.Option(..., help="Path to the rubric text file."),) if rubric_file is None else rubric_file
    api_key = (typer.Option(..., help="OpenAI API key."),) if api_key is None else api_key
    output = (typer.Option(..., help="Path to the output CSV file."),) if output is None else output
    scoring_format = (typer.Option("extended", help="Scoring format."),) if scoring_format is None else scoring_format

    client = OpenAI(api_key=api_key)
    story_text = read_file(story_file)
    question_text = read_file(question_file)
    rubric_text = read_file(rubric_file)

    if scoring_format not in ["extended", "item-specific", "short"]:
        raise typer.BadParameter("Format must be 'extended', 'item-specific', or 'short'")

    grade_responses(input_file, output, story_text, question_text, rubric_text, ai_model, client, scoring_format)
