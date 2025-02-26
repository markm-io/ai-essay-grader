import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def upload_jsonl(jsonl_path: str) -> str:
    """
    Upload JSONL file to OpenAI for fine-tuning.

    Args:
        jsonl_path: Path to the JSONL file to upload

    Returns:
        str: The file ID of the uploaded file

    """
    try:
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OpenAI API key is missing.")
            exit(1)

        with open(jsonl_path, "rb") as f:
            response = client.files.create(file=f, purpose="fine-tune")
            file_id = response.id
            print(f"✅ File uploaded successfully! File ID: {file_id}")
            return file_id
    except Exception as e:
        print(f"❌ Error uploading JSONL file: {e}")
        exit(1)
