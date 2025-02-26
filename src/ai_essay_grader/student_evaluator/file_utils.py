import sys
from pathlib import Path

import typer


def read_file(file_path: Path) -> str:
    """Read and return the content of a text file."""
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        typer.echo(f"Error reading file {file_path}: {e}", err=True)
        sys.exit(1)
