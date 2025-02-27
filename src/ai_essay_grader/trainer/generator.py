import json
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, ValidationError


# Define Pydantic model to ensure consistent response format
class GradingResponse(BaseModel):
    """
    Pydantic model representing the grading response format.

    Attributes:
        Score (int): The numerical score assigned to the student response
        Feedback (str): Detailed feedback explaining the score

    """

    Score: int
    Feedback: str


def validate_response(response_content: str) -> GradingResponse | None:
    """
    Validates and parses a JSON response string into a GradingResponse model.

    Args:
        response_content (str): JSON string containing score and feedback data

    Returns:
        GradingResponse | None: Validated response model if successful, None if validation fails

    Raises:
        ValidationError: If the response format doesn't match the GradingResponse model
        JSONDecodeError: If the response string is not valid JSON

    """
    try:
        response_dict = json.loads(response_content)
        return GradingResponse(**response_dict)
    except ValidationError as e:
        print(f"❌ Validation Error: {e.json()}")
        return None


def load_text_file(file_path: str | Path) -> str:
    """
    Load and normalize text file contents.

    Args:
        file_path: Path to the text file to load, as string or Path object

    Returns:
        str: File contents with normalized spaces

    Raises:
        FileNotFoundError: If the specified file does not exist

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read().strip()
        return text.replace("\u00a0", " ")  # Normalize spaces
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        exit(1)


def load_rubric_files(rubric_folder: str | Path, output_format: str) -> dict[str, Any]:
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

                        if output_format == "extended":
                            if category_name not in rubric_dict:
                                rubric_dict[category_name] = {}
                            rubric_dict[category_name][key] = value
                        else:
                            rubric_dict[key] = value

        except Exception as e:
            print(f"❌ Error reading '{rubric_file}': {e}")
            exit(1)

    return rubric_dict


def generate_jsonl(
    story_path: str | Path,
    question_path: str | Path,
    rubric_folder: str | Path,
    csv_path: str | Path,
    output_path: str | Path,
    output_format: str,
) -> str | Path:
    """
    Generates a JSONL file for fine-tuning based on input files and output format.

    Supported output_format values:
      - "extended": Includes detailed scoring for idea and language.
      - "item-specific" or "short": Returns "Score" and "Feedback" in a JSON string.

    Returns:
        str: Path to the generated JSONL file.

    """
    # Load text files with proper encoding
    story_text = load_text_file(story_path)
    question_text = load_text_file(question_path)
    rubric_dict = load_rubric_files(rubric_folder, output_format)  # Load rubric dynamically

    # Load CSV file
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error loading CSV file: {e}")
        exit(1)

    # Convert dataset into chat-based format
    chat_jsonl_data = []

    for _, row in df.iterrows():
        system_message = {"role": "system", "content": "AI Grader: Evaluate student responses based on rubric."}

        # Structured prompt to reduce token usage and dynamically insert rubric
        user_prompt = {
            "story": story_text,
            "question": question_text,
            "rubric": rubric_dict,  # Use structured or flattened rubric
            "student_response": row["Student Constructed Response"],
        }

        user_message = {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}

        # Format assistant response based on output_format
        if output_format == "extended":
            response_obj = {
                "Idea_Development_Score": str(row["Idea Development Score"]),
                "Idea_Development_Feedback": row["Idea Development Feedback"],
                "Language_Conventions_Score": str(row["Language Conventions Score"]),
                "Language_Conventions_Feedback": row["Language Conventions Feedback"],
            }
        elif output_format in ["item-specific", "short"]:
            response_obj = {
                "Score": str(row["Score"]),
                "Feedback": row["Feedback"],
            }
        else:
            print(f"❌ Error: Invalid output format '{output_format}'.")
            exit(1)

        # Validate the response using Pydantic
        validated_response = validate_response(json.dumps(response_obj))
        if not validated_response:
            print("⚠️ Skipping malformed response.")
            continue

        # Convert response to JSON string and append stop sequence
        assistant_response = {
            "role": "assistant",
            "content": json.dumps(validated_response.model_dump(), ensure_ascii=False) + " ###",
        }

        chat_jsonl_data.append({"messages": [system_message, user_message, assistant_response]})

    # Save JSONL file with proper encoding
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in chat_jsonl_data:
                clean_entry = json.dumps(entry, ensure_ascii=False).replace("\u00a0", " ")
                f.write(clean_entry + "\n")
        print(f"✅ JSONL file successfully generated: {output_path}")
    except Exception as e:
        print(f"❌ Error writing JSONL file: {e}")
        exit(1)

    return output_path
