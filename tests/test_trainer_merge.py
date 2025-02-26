import pytest

from ai_essay_grader.trainer.merge import merge_jsonl_files


def test_merge_success(tmp_path, capsys):
    # Create a temporary folder with two JSONL files.
    folder = tmp_path / "jsonl_folder"
    folder.mkdir()

    file1 = folder / "file1.jsonl"
    file2 = folder / "file2.jsonl"
    file1.write_text('{"key": "value1"}\n', encoding="utf-8")
    file2.write_text('{"key": "value2"}\n', encoding="utf-8")

    output_file = tmp_path / "merged.jsonl"
    result = merge_jsonl_files(str(folder), str(output_file))
    assert result == str(output_file)

    captured = capsys.readouterr().out
    # Check that the printed message contains the merging indicator (adjust to your function's output)
    assert "🔍 Merging" in captured

    # Verify that the merged file contains the content from both files.
    merged_lines = output_file.read_text(encoding="utf-8").splitlines()
    expected_lines = ['{"key": "value1"}', '{"key": "value2"}']
    assert sorted(merged_lines) == sorted(expected_lines)


def test_merge_no_files(tmp_path, capsys):
    # Create an empty folder.
    folder = tmp_path / "empty_folder"
    folder.mkdir()

    output_file = tmp_path / "merged.jsonl"
    with pytest.raises(SystemExit) as excinfo:
        merge_jsonl_files(str(folder), str(output_file))
    captured = capsys.readouterr().out
    # Expect the printed output to include an indicator of no files found.
    assert "❌ No JSONL files found in" in captured
    assert excinfo.value.code == 1


def test_merge_read_error(tmp_path, monkeypatch, capsys):
    # Create a folder with one JSONL file.
    folder = tmp_path / "jsonl_folder"
    folder.mkdir()
    file1 = folder / "file1.jsonl"
    file1.write_text('{"key": "value1"}\n', encoding="utf-8")

    # Monkeypatch open for reading to simulate a read error for file1.
    orig_open = open

    def fake_open_read(file, mode="r", *args, **kwargs):
        if str(file) == str(file1) and "r" in mode:
            raise Exception("Simulated read error")
        return orig_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open_read)

    output_file = tmp_path / "merged.jsonl"
    with pytest.raises(Exception) as excinfo:
        merge_jsonl_files(str(folder), str(output_file))
    assert "Simulated read error" in str(excinfo.value)


def test_merge_write_error(tmp_path, monkeypatch, capsys):
    # Create a folder with one JSONL file.
    folder = tmp_path / "jsonl_folder"
    folder.mkdir()
    file1 = folder / "file1.jsonl"
    file1.write_text('{"key": "value1"}\n', encoding="utf-8")

    # Monkeypatch open for writing the output file to simulate a write error.
    orig_open = open

    def fake_open_write(file, mode="r", *args, **kwargs):
        if str(file) == str(tmp_path / "merged.jsonl") and "w" in mode:
            raise Exception("Simulated write error")
        return orig_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open_write)

    output_file = tmp_path / "merged.jsonl"
    with pytest.raises(Exception) as excinfo:
        merge_jsonl_files(str(folder), str(output_file))
    assert "Simulated write error" in str(excinfo.value)
