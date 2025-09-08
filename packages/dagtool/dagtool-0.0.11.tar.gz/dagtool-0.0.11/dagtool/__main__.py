import json
import sys
from pathlib import Path
from textwrap import dedent
from typing import Any

import click
from airflow.configuration import conf
from pydantic import TypeAdapter

from .__about__ import __version__
from .models import DagModel


@click.group()
def cli() -> None:
    """Main DAG Tool CLI."""


@cli.command("version")
def version() -> None:
    """Return the current version of this DAG Tool package."""
    click.echo(__version__)
    sys.exit(0)


@cli.command("sync-vars")
@click.option(
    "--dags-folder",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    help="A DAGs folder.",
)
def sync_airflow_variable(dags_folder: Path | None = None):
    """Sync Airflow Variable that already set on the DAG folder with template
    DAG Tool.
    """
    click.echo("Sync Airflow Variable does not implement yet.")
    click.echo(
        dedent(
            """
            Steps:
            - Search Variable files reference the `.airflowignore` pattern.
            - Prepare variable with prefix name.
            - Sync to the target Airflow Variable.
            """.strip(
                "\n"
            )
        )
    )
    click.echo("NOTE:")
    click.echo(f"DAGs Folder: {dags_folder or conf.get('core', 'dags_folder')}")
    sys.exit(1)


@cli.command("render")
@click.option(
    "--path",
)
@click.option(
    "--name",
)
def render(name: str, path: Path):
    """Render DAG template with a specific name and path arguments to the
    Factory object.
    """
    click.echo("NOTE:")
    click.echo(f"- Name: {name}")
    click.echo(f"- Path: {path}")
    sys.exit(1)


@cli.command("validate")
@click.option(
    "--value",
)
def validate(value: str):
    """Validate DAG template with a specific name and path arguments to the
    Factory object.
    """
    click.echo("NOTE:")
    click.echo(f"- Value: {value}")
    sys.exit(1)


@cli.command("json-schema")
@click.option(
    "--file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=Path,
    ),
    help="A JSON schema file path that want to save.",
)
def build_json_schema(file: Path | None):
    """Build JSON Schema file from the current DagModel model."""
    click.echo("Start generate JSON Schema file for DAG Template.")
    json_schema: Any = TypeAdapter(DagModel).json_schema(by_alias=True)
    with (file or Path("./json-schema.json")).open(mode="w") as f:
        json.dump(json_schema, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    cli()
