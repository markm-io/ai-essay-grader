import pytest


@pytest.fixture(autouse=True)
def setup_openai_env(monkeypatch):
    """Set up a dummy OpenAI API key before running any tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-api-key-for-testing")
