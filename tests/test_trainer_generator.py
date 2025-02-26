import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from ai_essay_grader.trainer.generator import generate_jsonl, load_text_file


# Helper functions to create temporary text and CSV files.
def create_temp_text_file(tmp_path, filename, content):
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def create_temp_csv_file(tmp_path: Path, filename: str, data: dict[str, list[Any]]) -> str:
    df = pd.DataFrame(data)
    file_path = tmp_path / filename
    df.to_csv(file_path, index=False)
    return str(file_path)


# --- Tests for load_text_file ---


def test_load_text_file_success(tmp_path):
    file_path = create_temp_text_file(tmp_path, "test.txt", "Hello, world!")
    result = load_text_file(file_path)
    assert result == "Hello, world!"


def test_load_text_file_not_found(tmp_path, capsys):
    non_existent = tmp_path / "nonexistent.txt"
    with pytest.raises(SystemExit) as excinfo:
        load_text_file(str(non_existent))
    captured = capsys.readouterr().out
    assert f"Error: File '{non_existent}' not found." in captured
    assert excinfo.value.code == 1


# --- Tests for generate_jsonl ---


def test_generate_jsonl_extended(tmp_path, capsys):
    # Create temporary text files.
    story_file = create_temp_text_file(tmp_path, "story.txt", "Story text here.")
    question_file = create_temp_text_file(tmp_path, "question.txt", "Question text here.")
    rubric_file = create_temp_text_file(tmp_path, "rubric.txt", "Rubric text here.")

    # Create a CSV file with columns needed for "extended" format.
    data: dict[str, list[Any]] = {
        "Student Constructed Response": ["Response 1"],
        "Idea Development Score": [5],
        "Idea Development Feedback": ["Good ideas."],
        "Language Conventions Score": [4],
        "Language Conventions Feedback": ["Minor errors."],
    }
    csv_file = create_temp_csv_file(tmp_path, "data.csv", data)
    output_file = str(tmp_path / "output_extended.jsonl")

    result = generate_jsonl(story_file, question_file, rubric_file, csv_file, output_file, "extended")
    assert result == output_file

    captured = capsys.readouterr().out
    assert f"JSONL file successfully generated: {output_file}" in captured

    with open(output_file, encoding="utf-8") as f:
        lines = f.readlines()
    # Expect three messages for extended: system, user, and assistant.
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert "messages" in entry
    assert len(entry["messages"]) == 3
    system_msg = entry["messages"][0]
    assistant_msg = entry["messages"][2]
    assert system_msg["role"] == "system"
    assert "You are an AI trained" in system_msg["content"]
    # The assistant message should include evaluation details.
    assert "Idea Development Score:" in assistant_msg["content"]


def test_generate_jsonl_item_specific(tmp_path, capsys):
    # Create temporary text files.
    story_file = create_temp_text_file(tmp_path, "story.txt", "Another story text.")
    question_file = create_temp_text_file(tmp_path, "question.txt", "Another question text.")
    rubric_file = create_temp_text_file(tmp_path, "rubric.txt", "Another rubric text.")

    # Create CSV file with columns for item-specific format.
    data: dict[str, list[Any]] = {
        "Student Constructed Response": ["Response 2"],
        "Score": [10],
        "Feedback": ["Well done."],
    }
    csv_file = create_temp_csv_file(tmp_path, "data.csv", data)
    output_file = str(tmp_path / "output_item.jsonl")

    result = generate_jsonl(story_file, question_file, rubric_file, csv_file, output_file, "item-specific")
    assert result == output_file

    captured = capsys.readouterr().out
    assert f"JSONL file successfully generated: {output_file}" in captured

    with open(output_file, encoding="utf-8") as f:
        entry = json.loads(f.readline())
    # Expect three messages: system, user, and assistant.
    assert len(entry["messages"]) == 3
    # Verify roles.
    assert entry["messages"][0]["role"] == "system"
    assert entry["messages"][1]["role"] == "user"
    assistant_msg = entry["messages"][2]
    assert assistant_msg["role"] == "assistant"
    # Check that the assistant message includes Score and Feedback details.
    assert "Score:" in assistant_msg["content"]
    assert "Feedback:" in assistant_msg["content"]


def test_generate_jsonl_short(tmp_path, capsys):
    # "short" should behave like item-specific.
    story_file = create_temp_text_file(tmp_path, "story.txt", "Short story.")
    question_file = create_temp_text_file(tmp_path, "question.txt", "Short question.")
    rubric_file = create_temp_text_file(tmp_path, "rubric.txt", "Short rubric.")

    data: dict[str, list[Any]] = {
        "Student Constructed Response": ["Short response"],
        "Score": [8],
        "Feedback": ["Needs improvement."],
    }
    csv_file = create_temp_csv_file(tmp_path, "data.csv", data)
    output_file = str(tmp_path / "output_short.jsonl")

    result = generate_jsonl(story_file, question_file, rubric_file, csv_file, output_file, "short")
    assert result == output_file

    captured = capsys.readouterr().out
    assert f"JSONL file successfully generated: {output_file}" in captured

    with open(output_file, encoding="utf-8") as f:
        entry = json.loads(f.readline())
    # Expect three messages.
    assert len(entry["messages"]) == 3
    # Verify roles.
    assert entry["messages"][0]["role"] == "system"
    assert entry["messages"][1]["role"] == "user"
    assistant_msg = entry["messages"][2]
    assert assistant_msg["role"] == "assistant"
    # Check that the assistant message contains evaluation details.
    assert "Score:" in assistant_msg["content"]
    assert "Feedback:" in assistant_msg["content"]


def test_generate_jsonl_invalid_format(tmp_path, capsys):
    story_file = create_temp_text_file(tmp_path, "story.txt", "Story invalid.")
    question_file = create_temp_text_file(tmp_path, "question.txt", "Question invalid.")
    rubric_file = create_temp_text_file(tmp_path, "rubric.txt", "Rubric invalid.")

    data: dict[str, list[Any]] = {
        "Student Constructed Response": ["Invalid response"],
        "Score": [5],
        "Feedback": ["Bad."],
    }
    csv_file = create_temp_csv_file(tmp_path, "data.csv", data)
    output_file = str(tmp_path / "output_invalid.jsonl")

    with pytest.raises(SystemExit) as excinfo:
        generate_jsonl(story_file, question_file, rubric_file, csv_file, output_file, "not-a-valid-format")
    captured = capsys.readouterr().out
    assert "Invalid output format" in captured
    assert excinfo.value.code == 1


def test_generate_jsonl_csv_read_error(tmp_path, monkeypatch, capsys):
    def fake_read_csv(*args, **kwargs):
        raise Exception("Simulated CSV error")

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    story_file = create_temp_text_file(tmp_path, "story.txt", "Story for CSV error.")
    question_file = create_temp_text_file(tmp_path, "question.txt", "Question for CSV error.")
    rubric_file = create_temp_text_file(tmp_path, "rubric.txt", "Rubric for CSV error.")
    csv_file = str(tmp_path / "nonexistent.csv")
    output_file = str(tmp_path / "output_csv_error.jsonl")

    with pytest.raises(SystemExit) as excinfo:
        generate_jsonl(story_file, question_file, rubric_file, csv_file, output_file, "short")
    captured = capsys.readouterr().out
    assert "Error loading CSV file:" in captured
    assert "Simulated CSV error" in captured
    assert excinfo.value.code == 1


def test_generate_jsonl_write_error(tmp_path, monkeypatch, capsys):
    create_temp_text_file(tmp_path, "story.txt", "Story for write error.")
    create_temp_text_file(tmp_path, "question.txt", "Question for write error.")
    create_temp_text_file(tmp_path, "rubric.txt", "Rubric for write error.")
    data: dict[str, list[Any]] = {
        "Student Constructed Response": ["Response write error"],
        "Score": [3],
        "Feedback": ["Poor."],
    }
    create_temp_csv_file(tmp_path, "data.csv", data)
    str(tmp_path / "output_write_error.jsonl")

    def fake_open(*args, **kwargs):
        raise Exception("Simulated write error")
