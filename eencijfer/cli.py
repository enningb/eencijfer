"""Console script for eencijfer."""

from typing import Optional

import typer
from typing_extensions import Annotated

from eencijfer import APP_NAME, CONFIG_FILE, __version__
from eencijfer.eencijfer import ExportFormat, _convert_to_export_format
from eencijfer.init import _create_default_config
from eencijfer.qa import compare_eencijfer_files_and_definitions

app = typer.Typer(name="eencijfer", help="ETL-tool for Dutch eencijfer", no_args_is_help=True)


def _version_callback(value: bool) -> None:
    """Generates version nummber.

    Args:
        value (bool): boolean of there is a version

    Raises:
        typer.Exit: description
    """
    if value:
        typer.echo(f"{APP_NAME} v{__version__}")

        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit. Try running `eencijfer init`",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Eencijfer ETL-tool.

    Args:
        version (Optional[bool], optional): _description_. Defaults to typer.Option( None, "--version", "-v",
        help="Show the application's version and exit.", callback=_version_callback, is_eager=True, ).
    """
    # _version_callback()
    return


@app.command()
def init():
    """Initializes eencijfer-package."""
    _create_default_config(CONFIG_FILE)


@app.command()
def convert(
    export_format: ExportFormat = ExportFormat.parquet,
    use_column_converters: Annotated[
        bool, typer.Option("--use-column-converters/--not-use-column-converters", "-c/-C")
    ] = False,
):
    """Convert eencijfer-files to desired format."""
    _convert_to_export_format(export_format=export_format.value, use_column_converters=use_column_converters)


@app.command()
def qa():
    """Show overlap between eencijfer-files and definitions."""
    overlap = compare_eencijfer_files_and_definitions()
    typer.echo(overlap)
