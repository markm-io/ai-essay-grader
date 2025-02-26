from typer.testing import CliRunner

from ai_essay_grader.trainer.cli import trainer_app

runner = CliRunner()


# Dummy implementations for dependency functions.
def dummy_generate_jsonl(story, question, rubric, csv, output, question_type):
    return "dummy_output.jsonl"


def dummy_validate_jsonl(file):
    return True


def dummy_validate_jsonl_false(file):
    return False


def dummy_merge_jsonl_files(folder, output):
    return "dummy_merged.jsonl"


def dummy_upload_jsonl(file):
    return "dummy_file_id"


def dummy_create_fine_tuning_job(file_id):
    print(f"dummy fine-tuning job started for {file_id}")


# --- Tests for the 'generate' command ---


def test_generate_command_success(monkeypatch):
    monkeypatch.setattr("ai_essay_grader.trainer.cli.generate_jsonl", dummy_generate_jsonl)
    result = runner.invoke(
        trainer_app,
        [
            "generate",
            "--story",
            "story.txt",
            "--question",
            "question.txt",
            "--rubric",
            "rubric.txt",
            "--csv",
            "data.csv",
            "--output",
            "output.jsonl",
            "--question-type",
            "item-specific",
        ],
    )
    assert result.exit_code == 0
    assert "✅ JSONL file generated: dummy_output.jsonl" in result.output


def test_generate_command_bad_format():
    # When an invalid question_type is provided, a BadParameter error should occur.
    result = runner.invoke(
        trainer_app,
        [
            "generate",
            "--story",
            "story.txt",
            "--question",
            "question.txt",
            "--rubric",
            "rubric.txt",
            "--csv",
            "data.csv",
            "--output",
            "output.jsonl",
            "--question-type",
            "invalid_format",
        ],
    )
    assert result.exit_code != 0
    assert "Format must be 'extended', 'item-specific', or 'short'" in result.output


# --- Tests for the 'validate' command ---


def test_validate_command_success(monkeypatch):
    monkeypatch.setattr("ai_essay_grader.trainer.cli.validate_jsonl", dummy_validate_jsonl)
    result = runner.invoke(trainer_app, ["validate", "--file", "output.jsonl"])
    assert result.exit_code == 0
    assert "✅ JSONL file is valid!" in result.output


def test_validate_command_failure(monkeypatch):
    monkeypatch.setattr("ai_essay_grader.trainer.cli.validate_jsonl", dummy_validate_jsonl_false)
    result = runner.invoke(trainer_app, ["validate", "--file", "output.jsonl"])
    # When validation fails, no output is printed.
    assert result.exit_code == 0
    assert result.output.strip() == ""


# --- Test for the 'merge' command ---


def test_merge_command(monkeypatch):
    monkeypatch.setattr("ai_essay_grader.trainer.cli.merge_jsonl_files", dummy_merge_jsonl_files)
    result = runner.invoke(trainer_app, ["merge", "--folder", "jsonl_folder", "--output", "merged.jsonl"])
    assert result.exit_code == 0
    assert "✅ Merged JSONL file created: dummy_merged.jsonl" in result.output


# --- Test for the 'upload' command ---


def test_upload_command(monkeypatch):
    monkeypatch.setattr("ai_essay_grader.trainer.cli.upload_jsonl", dummy_upload_jsonl)
    result = runner.invoke(trainer_app, ["upload", "--file", "output.jsonl"])
    assert result.exit_code == 0
    assert "✅ JSONL file uploaded! File ID: dummy_file_id" in result.output


# --- Tests for the 'fine_tune' command ---


def test_fine_tune_command_with_file_success(monkeypatch):
    # When a file is provided and validation succeeds, it should upload and then start a fine-tuning job.
    monkeypatch.setattr("ai_essay_grader.trainer.cli.validate_jsonl", dummy_validate_jsonl)
    monkeypatch.setattr("ai_essay_grader.trainer.cli.upload_jsonl", dummy_upload_jsonl)
    monkeypatch.setattr("ai_essay_grader.trainer.cli.create_fine_tuning_job", dummy_create_fine_tuning_job)
    result = runner.invoke(trainer_app, ["fine-tune", "--file", "output.jsonl"])
    assert result.exit_code == 0
    assert "dummy fine-tuning job started for dummy_file_id" in result.output


def test_fine_tune_command_with_file_invalid(monkeypatch):
    # When validation fails for the provided file, nothing further happens.
    monkeypatch.setattr("ai_essay_grader.trainer.cli.validate_jsonl", dummy_validate_jsonl_false)

    # We also set create_fine_tuning_job to a dummy that would print something if called.
    def dummy_no_call(file_id):
        print("should not be called")

    monkeypatch.setattr("ai_essay_grader.trainer.cli.create_fine_tuning_job", dummy_no_call)
    result = runner.invoke(trainer_app, ["fine-tune", "--file", "output.jsonl"])
    assert result.exit_code == 0
    # Expect no output since the validation failed and no fine-tuning job was started.
    assert result.output.strip() == ""


def test_fine_tune_command_with_file_id(monkeypatch):
    # When a file_id is provided (and no file), it should directly start the fine-tuning job.
    monkeypatch.setattr("ai_essay_grader.trainer.cli.create_fine_tuning_job", dummy_create_fine_tuning_job)
    result = runner.invoke(trainer_app, ["fine-tune", "--file-id", "custom_file_id"])
    assert result.exit_code == 0
    assert "dummy fine-tuning job started for custom_file_id" in result.output


def test_fine_tune_command_without_file_or_file_id():
    # When neither --file nor --file-id is provided, an error message is echoed.
    result = runner.invoke(trainer_app, ["fine-tune"])
    assert result.exit_code == 0
    assert "❌ You must provide either --file or --file-id" in result.output
