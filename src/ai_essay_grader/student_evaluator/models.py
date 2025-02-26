from pydantic import BaseModel


class ResponseScore(BaseModel):
    """
    A model representing a basic scoring response.

    Attributes:
        score (int): The overall numerical score for the response
        feedback (str): Detailed feedback explaining the score

    """

    score: int
    feedback: str


class ExtendedResponseScore(BaseModel):
    """
    A model representing a detailed scoring response with separate categories.

    Attributes:
        idea_development_score (int): Score for the development and organization of ideas
        idea_development_feedback (str): Detailed feedback on idea development
        language_conventions_score (int): Score for grammar, mechanics, and language use
        language_conventions_feedback (str): Detailed feedback on language conventions

    """

    idea_development_score: int
    idea_development_feedback: str
    language_conventions_score: int
    language_conventions_feedback: str
