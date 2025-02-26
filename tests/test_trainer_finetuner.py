import pytest

from ai_essay_grader.trainer.finetuner import create_fine_tuning_job


def test_missing_api_key(monkeypatch, capsys):
    # Remove the API key from the environment.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(SystemExit) as excinfo:
        create_fine_tuning_job("dummy_file_id")
    captured = capsys.readouterr().out
    assert "Error: OpenAI API key is missing." in captured
    assert excinfo.value.code == 1


def test_create_fine_tuning_job_success(monkeypatch, capsys):
    # Set a dummy API key.
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_key")

    # Define dummy classes to simulate a successful API call.
    class DummyResponse:
        id = "job_1234"

    class DummyJobs:
        def create(self, training_file, model):
            # Check that the proper arguments are passed.
            assert training_file == "dummy_file_id"
            assert model == "gpt-4o-mini-2024-07-18"
            return DummyResponse()

    class DummyFineTuning:
        def __init__(self):
            self.jobs = DummyJobs()

    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.fine_tuning = DummyFineTuning()

    # Monkeypatch OpenAI so that it returns our dummy client.
    monkeypatch.setattr("ai_essay_grader.trainer.finetuner.OpenAI", lambda api_key: DummyClient(api_key))

    # Call the function and capture its output.
    job_id = create_fine_tuning_job("dummy_file_id")
    captured = capsys.readouterr().out
    assert "🚀 Fine-tuning job started! Job ID: job_1234" in captured
    assert job_id == "job_1234"


def test_create_fine_tuning_job_exception(monkeypatch, capsys):
    # Set a dummy API key.
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_key")

    # Define dummy classes that raise an exception during job creation.
    class DummyJobs:
        def create(self, training_file, model):
            raise Exception("Test Exception")

    class DummyFineTuning:
        def __init__(self):
            self.jobs = DummyJobs()

    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.fine_tuning = DummyFineTuning()

    monkeypatch.setattr("ai_essay_grader.trainer.finetuner.OpenAI", lambda api_key: DummyClient(api_key))

    # The exception in the try block should trigger a SystemExit.
    with pytest.raises(SystemExit) as excinfo:
        create_fine_tuning_job("dummy_file_id")
    captured = capsys.readouterr().out
    assert "Error creating fine-tuning job: Test Exception" in captured
    assert excinfo.value.code == 1
