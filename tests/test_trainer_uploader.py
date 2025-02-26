import pytest

from ai_essay_grader.trainer.uploader import upload_jsonl


# Test when the OpenAI API key is missing.
def test_missing_api_key(monkeypatch, capsys):
    # Remove the API key from the environment.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # Call the function with any file path (it won't get that far).
    with pytest.raises(SystemExit) as excinfo:
        upload_jsonl("dummy.jsonl")
    captured = capsys.readouterr().out
    assert "❌ Error: OpenAI API key is missing." in captured
    assert excinfo.value.code == 1


# Test a successful file upload.
def test_successful_upload(tmp_path, monkeypatch, capsys):
    # Set the API key so that the check passes.
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_key")
    # Create a temporary JSONL file.
    file_path = tmp_path / "test.jsonl"
    file_path.write_text('{"dummy": "data"}\n', encoding="utf-8")

    # Define a dummy response object.
    class DummyResponse:
        id = "dummy_file_id"

    # Monkeypatch the client's files.create method.
    def dummy_create(file, purpose):
        # You could add assertions here on the file mode if needed.
        return DummyResponse()

    monkeypatch.setattr("ai_essay_grader.trainer.uploader.client.files.create", dummy_create)

    result = upload_jsonl(str(file_path))
    captured = capsys.readouterr().out
    assert "✅ File uploaded successfully! File ID: dummy_file_id" in captured
    assert result == "dummy_file_id"


# Test when the API call raises an exception.
def test_upload_api_exception(tmp_path, monkeypatch, capsys):
    # Ensure the API key is set.
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_key")
    # Create a temporary JSONL file.
    file_path = tmp_path / "test.jsonl"
    file_path.write_text('{"dummy": "data"}\n', encoding="utf-8")

    # Monkeypatch the client's files.create to raise an exception.
    def dummy_create(file, purpose):
        raise Exception("Simulated upload error")

    monkeypatch.setattr("ai_essay_grader.trainer.uploader.client.files.create", dummy_create)

    with pytest.raises(SystemExit) as excinfo:
        upload_jsonl(str(file_path))
    captured = capsys.readouterr().out
    assert "❌ Error uploading JSONL file: Simulated upload error" in captured
    assert excinfo.value.code == 1


# Test when the specified JSONL file is not found.
def test_upload_file_not_found(monkeypatch, capsys):
    # Ensure the API key is set.
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_key")
    # Use a path that does not exist.
    non_existent_path = "nonexistent_file.jsonl"

    with pytest.raises(SystemExit) as excinfo:
        upload_jsonl(non_existent_path)
    captured = capsys.readouterr().out
    # The exception message should include a file-not-found error.
    assert "❌ Error uploading JSONL file:" in captured
    assert "No such file or directory" in captured or "cannot find" in captured
    assert excinfo.value.code == 1
