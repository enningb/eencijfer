"""Console script for eencijfer."""

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from eencijfer import APP_NAME, CONFIG_FILE, __version__
from eencijfer.assets.cohorten import create_cohorten_met_indicatoren
from eencijfer.assets.eencijfer import _create_eencijfer_df
from eencijfer.assets.eindexamencijfers import _create_eindexamencijfer_df
from eencijfer.eencijfer import ExportFormat, _convert_to_export_format
from eencijfer.init import _create_default_config
from eencijfer.io.file import _save_to_file
from eencijfer.pii import _replace_all_pgn_with_pseudo_id_remove_pii_local_id
from eencijfer.qa import compare_eencijfer_files_and_definitions
from eencijfer.settings import config

app = typer.Typer(name="eencijfer", help="ETL-tool for Dutch eencijfer", no_args_is_help=True)


def _version_callback(value: bool) -> None:
    """Gives version nummber.

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
    return None


@app.command()
def init():
    """Initializes eencijfer-package."""
    _create_default_config(CONFIG_FILE)


@app.command()
def convert(
    export_format: ExportFormat = ExportFormat.parquet,
    use_column_converters: Annotated[bool, typer.Option("--use-column-converters/--not-use-column-converters", "-c/-C")] = True,
    remove_pii: Annotated[bool, typer.Option("--remove-pii/--do-not-remove-pii", "-p/-P")] = True,
    add_local_id: Annotated[bool, typer.Option("--add-local-id/--do-not-add-local-id", "-s/-S")] = False,
):
    """Convert eencijfer-files to desired exportformat, with or without PII."""

    result_dir = config.getpath('default', 'result_dir')
    if not result_dir.is_dir():
        Path(result_dir).mkdir(parents=True, exist_ok=True)

    _convert_to_export_format(export_format=export_format.value, use_column_converters=use_column_converters)

    _replace_all_pgn_with_pseudo_id_remove_pii_local_id(
        export_format=export_format, remove_pii=remove_pii, add_local_id=add_local_id
    )


@app.command()
def qa():
    """Show overlap between eencijfer-files and definitions."""
    overlap = compare_eencijfer_files_and_definitions()
    typer.echo(overlap)
    typer.echo(Path().absolute())


@app.command()
def create_assets(export_format: ExportFormat = ExportFormat.parquet):
    """Create data-assets and save them to assests-directory."""
    assets_dir = config.getpath('default', 'assets_dir')

    eencijfer = _create_eencijfer_df()
    _save_to_file(eencijfer, dir=assets_dir, fname='eencijfer', export_format='parquet')
    cohorten = create_cohorten_met_indicatoren()
    _save_to_file(cohorten, dir=assets_dir, fname='cohorten', export_format='parquet')
    eindexamencijfers = _create_eindexamencijfer_df()
    _save_to_file(
        eindexamencijfers,
        dir=assets_dir,
        fname='eindexamencijfers',
        export_format='parquet',
    )
