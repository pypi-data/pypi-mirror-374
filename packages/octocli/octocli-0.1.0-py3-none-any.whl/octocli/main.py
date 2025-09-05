from typer import Typer

from .commands import model

app = Typer(name="octocli")

app.add_typer(model.app, name="model")
