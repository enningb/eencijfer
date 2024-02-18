"""Settings for eencijfer."""
import configparser
import logging

import typer

from eencijfer import CONFIG_FILE

logger = logging.getLogger(__name__)

try:
    config = configparser.ConfigParser()
    # config.optionxform = str  # So capitals stay capitals
    config.read(CONFIG_FILE)
    # # Directory containing all the .ASC files that are in LEESMIJ.zip:
except Exception as e:
    typer.echo("-----------------------------")
    typer.echo("    There is not a valid config-file at: %s" % CONFIG_FILE)
    typer.echo("    Try to run:")
    typer.echo("        eencijfer init")
    typer.echo("-----------------------------")
    typer.echo("")
    typer.echo(" The erro was: ")
    typer.echo(f"{e}")
    typer.echo("-----------------------------")
