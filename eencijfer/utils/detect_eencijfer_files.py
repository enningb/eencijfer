"""Detect eencijfer-files."""

import logging
from pathlib import Path
from typing import Optional

import typer

from eencijfer.settings import config

logger = logging.getLogger(__name__)


def _get_list_of_eencijfer_files_in_dir() -> Optional[list]:
    """Gets list of eencijfer-files that are in eencijfer_dir.

    Get a list of eencijfer-files in the given source_dir (in config-file). Gives a list
    of files that match the names of the files in the definition-dir.

    Args:
        config (configparser.ConfigParser, optional): _description_. Defaults to config.

    Returns:
        Optional[list]: List of files that are recognized as eencijfer-files.
    """
    source_dir = config.getpath('default', 'source_dir')
    files = None
    try:
        logger.debug("Getting list of files ending with '.asc'...")
        asc_files = [p for p in source_dir.iterdir() if p.suffix.lower() == '.asc']
        logger.debug("...looking for file starting with 'EV'...")
        files = asc_files + [p for p in source_dir.iterdir() if p.stem.startswith('EV')]
        if len(files) == 0:
            typer.echo(f"No files found that in {source_dir} that could be eencijfer-files. Aborting...")
            raise typer.Exit()
        else:
            typer.echo(f"Found {len(files)} files in `{source_dir}` that might be eencijfer-files.")
    except FileNotFoundError:
        typer.echo(f'No files found. Does the directory `{source_dir}` exist?')
        raise typer.Exit()

    return files


def _get_eencijfer_datafile(source_dir: Path) -> Optional[str]:
    """Get the name of the eencijfer-file in the given directory.

    Args:
        source_dir (Path): path to source_dir.

    Returns:
        str: name of file.
    """
    logger.debug("Set variable eencijfer_datafile to None.")
    eencijfer_datafile = None
    try:
        logger.debug("Get the name of the first file that starts with `EV`.")
        eencijfer_datafile = [file.stem for file in Path(source_dir).iterdir() if "EV" in file.stem][0]
        logger.debug(f"In {source_dir} the file {eencijfer_datafile} will be used as eencijfer.")

    except IndexError:
        logger.debug(f"In {source_dir} there is no file starting with 'EV' so it is assumed there is no eencijfer...")
        logger.debug(f"...move this file to {source_dir} or change option 'eencijfer_datafile' in config-file.")
    except FileNotFoundError:
        logger.debug(f"The directory `{source_dir}` does not seem to exist...")

    return eencijfer_datafile


def _get_eindexamen_datafile(source_dir: Path) -> Optional[str]:
    """Get the name of the file with the eindexamen-scores.

    Args:
        source_dir (Path): path to directory containing eencijfer-files.

    Returns:
        str: Name of eindexamenfile.
    """
    eindexamen_datafile = None

    try:
        eindexamen_datafile = [file.stem for file in Path(source_dir).iterdir() if "VAKH" in file.stem][0]
        logger.debug(f"In {source_dir} the file {source_dir} will be used as eindexamenfile.")

    except IndexError:
        logger.critical(f"In {source_dir} there is no file starting with 'VAKH' ")
        logger.critical("so it is assumed there is no eindexamenfile...")
        logger.critical(f"...move this file to {source_dir} or change option 'eindexamen_datafile' in config-file.")
    return eindexamen_datafile
