import json
from pathlib import Path

import pandas as pd


def load_text_file(file_path: str | Path) -> str:
    """
    Load a text file and return its contents as a string.

    Args:
        file_path: Path to the text file to load

    Returns:
        str: Contents of the text file

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        exit(1)


def generate_jsonl(
    story_path: str | Path,
    question_path: str | Path,
    rubric_path: str | Path,
    csv_path: str | Path,
    output_path: str | Path,
    output_format: str,
) -> str | Path:
    """
    Generate a JSONL file for fine-tuning based on input files and output format.

    Args:
        story_path: Path to the story text file
        question_path: Path to the question text file
        rubric_path: Path to the rubric text file
        csv_path: Path to the CSV file with student responses
        output_path: Path where the JSONL file will be saved
        output_format: Format of the output ("extended", "item-specific", or "short")

    Returns:
        str: Path to the generated JSONL file

    """
    # Load files
    story_text = load_text_file(story_path)
    question_text = load_text_file(question_path)
    rubric_text = load_text_file(rubric_path)

    # Load CSV file
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error loading CSV file: {e}")
        exit(1)

    # Convert dataset into chat-based format
    chat_jsonl_data = []

    for _, row in df.iterrows():
        chat_entry = {
            "messages": [
                {"role": "system", "content": "You are an AI trained to evaluate student responses based on a rubric."},
                {
                    "role": "user",
                    "content": (
                        f"Story:\n{story_text}\n\n"
                        f"Question:\n{question_text}\n\n"
                        f"Rubric:\n{rubric_text}\n\n"
                        f"Student Response:\n{row['Student Constructed Response']}"
                    ),
                },
            ]
        }

        # Format assistant response based on output_format
        if output_format == "extended":
            assistant_response = {
                "role": "assistant",
                "content": (
                    f"Idea Development Score: {row['Idea Development Score']}\n"
                    f"Idea Development Feedback: {row['Idea Development Feedback']}\n"
                    f"Language Conventions Score: {row['Language Conventions Score']}\n"
                    f"Language Conventions Feedback: {row['Language Conventions Feedback']}"
                ),
            }
        elif output_format in ["item-specific", "short"]:
            assistant_response = {
                "role": "assistant",
                "content": (f"Score: {row['Score']}\nFeedback: {row['Feedback']}"),
            }
        else:
            print(
                f"❌ Error: Invalid output format '{output_format}'. "
                f"Choose from 'extended', 'item-specific', or 'short'."
            )
            exit(1)

        chat_entry["messages"].append(assistant_response)
        chat_jsonl_data.append(chat_entry)

    # Save as JSONL file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in chat_jsonl_data:
                json.dump(entry, f)
                f.write("\n")
        print(f"✅ JSONL file successfully generated: {output_path}")
    except Exception as e:
        print(f"❌ Error writing JSONL file: {e}")
        exit(1)

    return output_path
