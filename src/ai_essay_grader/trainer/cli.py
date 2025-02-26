from typing import Optional

import typer

from . import create_fine_tuning_job, generate_jsonl, merge_jsonl_files, upload_jsonl, validate_jsonl

trainer_app = typer.Typer(help="Generate, validate, merge, upload, and fine-tune JSONL files.")


@trainer_app.command()
def generate(
    story: str = typer.Option(..., help="Path to the story.txt file"),
    question: str = typer.Option(..., help="Path to the question.txt file"),
    rubric: str = typer.Option(..., help="Path to the rubric.txt file"),
    csv: str = typer.Option(..., help="Path to the model_testing.csv file"),
    output: str = typer.Option("fine_tuning.jsonl", help="Output JSONL file name"),
    question_type: str = typer.Option(..., help="Output format: extended, item-specific, or short."),
) -> None:
    """Generate JSONL file from input files."""
    if question_type not in ["extended", "item-specific", "short"]:
        raise typer.BadParameter("Format must be 'extended', 'item-specific', or 'short'")
    jsonl_file = generate_jsonl(story, question, rubric, csv, output, question_type)
    typer.echo(f"✅ JSONL file generated: {jsonl_file}")


@trainer_app.command()
def validate(file: str = typer.Option(..., help="Path to the JSONL file to validate")) -> None:
    """Validate a JSONL file."""
    if validate_jsonl(file):
        typer.echo("✅ JSONL file is valid!")


@trainer_app.command()
def merge(
    folder: str = typer.Option(..., help="Path to the folder containing JSONL files"),
    output: str = typer.Option("merged_fine_tuning.jsonl", help="Output merged JSONL file name"),
) -> None:
    """Merge all JSONL files in a folder into one."""
    merged_file = merge_jsonl_files(folder, output)
    typer.echo(f"✅ Merged JSONL file created: {merged_file}")


@trainer_app.command()
def upload(
    file: str = typer.Option(..., help="Path to the JSONL file to upload"),
    api_key: Optional[str] = typer.Option(None, help="OpenAI API key"),
) -> None:
    """Upload a validated JSONL file to OpenAI."""
    file_id = upload_jsonl(file, api_key)
    typer.echo(f"✅ JSONL file uploaded! File ID: {file_id}")


@trainer_app.command()
def fine_tune(
    file: Optional[str] = typer.Option(None, help="Path to a validated JSONL file for uploading & fine-tuning"),
    file_id: Optional[str] = typer.Option(None, help="Existing file ID to use for fine-tuning"),
    api_key: Optional[str] = typer.Option(None, help="OpenAI API key"),
) -> None:
    """Start a fine-tuning job using OpenAI."""
    if file:
        if validate_jsonl(file):
            file_id = upload_jsonl(file, api_key)
            create_fine_tuning_job(file_id)
    elif file_id:
        create_fine_tuning_job(file_id)
    else:
        typer.echo("❌ You must provide either --file or --file-id", err=True)
