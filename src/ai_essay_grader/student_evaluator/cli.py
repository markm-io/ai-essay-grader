from pathlib import Path

import typer

from .file_utils import load_rubric_files, load_story_files, read_file
from .grader import grade_responses

grader_app = typer.Typer()


@grader_app.command()
def main(
    input_file: Path = typer.Option(..., help="Path to the input CSV file."),
    ai_model: str = typer.Option(None, help="OpenAI model identifier."),
    story_folder: Path = typer.Option(..., help="Path to the story text file."),
    question_file: Path = typer.Option(..., help="Path to the question text file."),
    rubric_folder: Path = typer.Option(..., help="Path to the rubric folder."),
    api_key: str = typer.Option(..., help="OpenAI API key."),
    output: Path = typer.Option(..., help="Path to the output CSV file."),
    scoring_format: str = typer.Option(..., help="Scoring format."),
) -> None:
    """
    CLI entry point for grading student responses.

    Args:
        input_file (Path): CSV file containing student responses to be graded
        ai_model (str): Identifier for the OpenAI model to be used
        story_folder (Path): Folder containing the stories or passages
        question_file (Path): Text file containing the questions
        rubric_folder (Path): Folder containing the grading rubric text files
        api_key (str): OpenAI API authentication key
        output (Path): Destination CSV file for graded responses
        scoring_format (str): Format for score presentation (extended/short)

    """
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)
    story_dict = load_story_files(story_folder)
    question_text = read_file(question_file)
    rubric_text = load_rubric_files(rubric_folder, scoring_format)

    if scoring_format not in ["extended", "item-specific", "short"]:
        raise typer.BadParameter("Format must be 'extended', 'item-specific', or 'short'")

    grade_responses(input_file, output, story_dict, question_text, rubric_text, ai_model, client, scoring_format)
