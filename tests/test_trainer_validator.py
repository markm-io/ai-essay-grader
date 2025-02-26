import json

import pytest

from ai_essay_grader.trainer.validator import validate_jsonl


# Helper function to create a temporary JSONL file with given content.
def create_temp_jsonl(tmp_path, filename, content):
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def test_valid_jsonl(tmp_path, capsys):
    # Create a valid JSONL file with one line that satisfies all conditions.
    valid_entry = {
        "messages": [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Idea Development Score: 5\nLanguage Conventions Score: 4"},
        ]
    }
    file_path = create_temp_jsonl(tmp_path, "valid.jsonl", json.dumps(valid_entry) + "\n")
    result = validate_jsonl(file_path)
    captured = capsys.readouterr().out
    assert "✅ JSONL file" in captured
    assert result is True


def test_read_error(tmp_path, monkeypatch, capsys):
    # Simulate a file read error by monkeypatching open to raise an exception.
    def fake_open(*args, **kwargs):
        raise Exception("Simulated read error")

    monkeypatch.setattr("builtins.open", fake_open)
    file_path = str(tmp_path / "dummy.jsonl")
    with pytest.raises(SystemExit) as excinfo:
        validate_jsonl(file_path)
    captured = capsys.readouterr().out
    assert "❌ Error reading JSONL file: Simulated read error" in captured
    assert excinfo.value.code == 1


def test_invalid_json_format(tmp_path, capsys):
    # Create a file with a line that is not valid JSON.
    file_path = create_temp_jsonl(tmp_path, "invalid_format.jsonl", "not a json\n")
    with pytest.raises(SystemExit) as excinfo:
        validate_jsonl(file_path)
    captured = capsys.readouterr().out
    assert "❌ Error: Invalid JSON format on line 1" in captured
    assert excinfo.value.code == 1


def test_missing_messages_key(tmp_path, capsys):
    # Create a file with JSON that does not contain the required "messages" key.
    file_path = create_temp_jsonl(tmp_path, "missing_messages.jsonl", json.dumps({"not_messages": 123}) + "\n")
    with pytest.raises(SystemExit) as excinfo:
        validate_jsonl(file_path)
    captured = capsys.readouterr().out
    assert "❌ Error: Missing 'messages' key" in captured
    assert "(line 1)" in captured
    assert excinfo.value.code == 1


def test_messages_not_list(tmp_path, capsys):
    # Create a file with JSON where the "messages" key is not a list.
    file_path = create_temp_jsonl(tmp_path, "not_list.jsonl", json.dumps({"messages": "not a list"}) + "\n")
    with pytest.raises(SystemExit) as excinfo:
        validate_jsonl(file_path)
    captured = capsys.readouterr().out
    assert "❌ Error: 'messages' should be a list" in captured
    assert "(line 1)" in captured
    assert excinfo.value.code == 1


def test_incorrect_roles_sequence(tmp_path, capsys):
    # Create a file with JSON where the roles sequence is not as expected.
    entry = {
        "messages": [
            {"role": "system", "content": "System message"},
            {"role": "assistant", "content": "Assistant message"},
            {"role": "user", "content": "User message"},
        ]
    }
    file_path = create_temp_jsonl(tmp_path, "wrong_roles.jsonl", json.dumps(entry) + "\n")
    with pytest.raises(SystemExit) as excinfo:
        validate_jsonl(file_path)
    captured = capsys.readouterr().out
    assert "❌ Error: Incorrect roles sequence in entry 1:" in captured
    assert excinfo.value.code == 1


def test_missing_labels_in_assistant(tmp_path, capsys):
    # Create a file where the assistant's message does not include the expected labels.
    entry = {
        "messages": [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Some response without expected labels"},
        ]
    }
    file_path = create_temp_jsonl(tmp_path, "missing_labels.jsonl", json.dumps(entry) + "\n")
    with pytest.raises(SystemExit) as excinfo:
        validate_jsonl(file_path)
    captured = capsys.readouterr().out
    assert "❌ Error: Missing expected labels in assistant response in entry 1" in captured
    assert excinfo.value.code == 1
