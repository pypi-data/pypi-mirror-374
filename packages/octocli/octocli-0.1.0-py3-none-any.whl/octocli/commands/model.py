from pathlib import Path
from typing import Annotated

from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console
from rich.prompt import Prompt
from typer import Option, Typer

from ..schemas import ColumnSchema, ModelConfig

app = Typer()
console = Console()


def parse_type(type_: str) -> str:
    datatypes = {
        "bool": ["Boolean"],
        "str": ["String", "Text"],
        "float": ["Double", "Float", "Numeric"],
        "datetime": ["Date", "Time", "DateTime"],
        "int": ["BigInteger", "Integer", "SmallInteger"],
    }

    if type_ not in datatypes:
        console.print(f"[bold red]Python type '{type_}' not supported![/]")
        raise

    sql_type = Prompt.ask(
        "Select the SQL generic datatype",
        choices=datatypes[type_],
    )

    return sql_type


def get_columns() -> list[ColumnSchema]:
    console.print("Type 'end' to finish")
    cols = []

    while True:
        col_name = Prompt.ask("Column name", case_sensitive=False)
        if col_name == "end":
            break

        col_type = Prompt.ask("Column type", choices=["str", "int", "float", "bool"])

        column = {"name": col_name, "type_": col_type, "sql_type": parse_type(col_type)}
        cols.append(column)

    return cols


def create_file(config: ModelConfig) -> None:
    env = Environment(
        loader=PackageLoader("octocli"),
        autoescape=select_autoescape(),
    )

    path = f"models/{'duplicate' if config.is_duplicate else 'standard'}.py.j2"
    template = env.get_template(path)

    buffer = template.render(config.model_dump())

    try:
        curr_dir = Path().cwd()
        models_dir = curr_dir / "models"

        console.print(f"Attempting to create directory: {models_dir}")
        models_dir.mkdir()
        console.print("New directory '/models' created.")
    except FileExistsError:
        pass
    except Exception as e:
        console.print("[bold red]Unexpected error occured[/]")
        console.print(e)
        raise

    with open(f"models/{config.model_name}.py", "w") as file:
        file.write(buffer)


@app.command()
def create(
    model_name: str,
    duplicate: Annotated[
        bool,
        Option(help="Create a duplicate table model representation."),
    ] = False,
) -> None:
    class_name = model_name.title().replace("_", "")

    cols = get_columns() if not duplicate else []

    config = ModelConfig(
        model_name=model_name,
        class_name=class_name,
        is_duplicate=duplicate,
        columns=cols,
    )

    create_file(config)
