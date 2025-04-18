"""Make the CLI runnable using python -m ai_essay_grader."""

from typer import Typer

from .student_evaluator.cli import grader_app
from .trainer.cli import trainer_app

app = Typer()

app.add_typer(grader_app, name="grader")
app.add_typer(trainer_app, name="trainer")
