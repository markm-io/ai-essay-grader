import sys
from pathlib import Path
from typing import Any

import typer


def read_file(file_path: Path) -> str:
    """Read and return the content of a text file."""
    try:
        return file_path.read_text(encoding="utf-8").strip().replace("\u00a0", " ")  # Normalize spaces
    except Exception as e:
        typer.echo(f"Error reading file {file_path}: {e}", err=True)
        sys.exit(1)


def load_rubric_files(rubric_folder: str | Path, scoring_format: str) -> dict[str, Any]:
    """
    Loads multiple rubric files from a folder and organizes them into a dictionary.

    - If `output_format == "extended"`, the rubric is **structured by categories**.
    - Otherwise, the rubric is **flattened** to only contain `score_3`, `score_2`, etc.

    Returns:
        dict: A structured or flattened rubric dictionary.

    """
    rubric_dict: dict[str, Any] = {}

    rubric_folder = Path(rubric_folder)

    if not rubric_folder.exists() or not rubric_folder.is_dir():
        print(f"❌ Error: Rubric folder '{rubric_folder}' not found or not a directory.")
        exit(1)

    for rubric_file in rubric_folder.glob("*.txt"):
        category_name = rubric_file.stem.replace("_", " ")

        try:
            with open(rubric_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    if " - " in line:
                        key, value = line.split(" - ", 1)
                        key = key.strip()
                        value = value.strip()

                        if scoring_format == "extended":
                            if category_name not in rubric_dict:
                                rubric_dict[category_name] = {}
                            rubric_dict[category_name][key] = value
                        else:
                            rubric_dict[key] = value

        except Exception as e:
            print(f"❌ Error reading '{rubric_file}': {e}")
            exit(1)

    return rubric_dict


def load_story_files(story_folder: str | Path) -> dict[str, str]:
    """
    Loads multiple story files from a folder and organizes them into a dictionary.

    Returns:
        dict: A dictionary mapping "Story 1", "Story 2", etc., to story content.

    """
    story_dict: dict[str, str] = {}

    story_folder = Path(story_folder)

    if not story_folder.exists() or not story_folder.is_dir():
        print(f"❌ Error: Story folder '{story_folder}' not found or not a directory.")
        exit(1)

    story_files = sorted(story_folder.glob("*.txt"))  # Sort for consistent ordering

    for idx, story_file in enumerate(story_files, start=1):
        try:
            with open(story_file, encoding="utf-8") as f:
                story_text = f.read().strip()
            story_dict[f"Story {idx}"] = story_text.replace("\u00a0", " ")  # Normalize spaces
        except Exception as e:
            print(f"❌ Error reading '{story_file}': {e}")
            exit(1)

    return story_dict
