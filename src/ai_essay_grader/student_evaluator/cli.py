from pathlib import Path

import typer
from openai import OpenAI

from .file_utils import read_file
from .grader import grade_responses

grader_app = typer.Typer()


@grader_app.command()
def main(
    input_file: Path = typer.Option(..., help="Path to the input CSV file."),
    ai_model: str = typer.Option(..., help="OpenAI model identifier."),
    story_file: Path = typer.Option(..., help="Path to the story text file."),
    question_file: Path = typer.Option(..., help="Path to the question text file."),
    rubric_file: Path = typer.Option(..., help="Path to the rubric text file."),
    api_key: str = typer.Option(..., help="OpenAI API key."),
    output: Path = typer.Option(..., help="Path to the output CSV file."),
    scoring_format: str = typer.Option("extended", help="Scoring format."),
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
    client = OpenAI(api_key=api_key)
    story_text = read_file(story_file)
    question_text = read_file(question_file)
    rubric_text = read_file(rubric_file)

    if scoring_format not in ["extended", "item-specific", "short"]:
        raise typer.BadParameter("Format must be 'extended', 'item-specific', or 'short'")

    grade_responses(input_file, output, story_text, question_text, rubric_text, ai_model, client, scoring_format)
