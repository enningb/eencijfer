"""Console script for eencijfer."""

import typer

from eencijfer import CONFIG_FILE

app = typer.Typer(
    name="eencijfer",
    help="ETL-tool for Dutch eencijfer",
)


@app.callback()
def callback():
    """ETL-tool for Dutch eencijfer."""


# create commandline tool with code like below:
@app.command()
def example_command():
    """Print configfile path."""
    typer.echo(f"The configfile is at: {CONFIG_FILE} ")
