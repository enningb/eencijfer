"""Initialize eencijfer config file."""

import configparser
import logging
from pathlib import Path
from typing import Optional

import typer

from eencijfer import CONFIG_FILE, PACKAGE_PROVIDED_IMPORT_DEFINTIONS_DIR, __app_name__
from eencijfer.eencijfer import _get_list_of_eencijfer_files_in_dir

logger = logging.getLogger(__name__)


default_assets_dir = Path.home() / __app_name__ / "assets"
default_result_dir = Path.home() / __app_name__ / "result"
default_source_dir = Path.home() / __app_name__ / "eencijfer"
default_import_definitions_dir = PACKAGE_PROVIDED_IMPORT_DEFINTIONS_DIR


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
        logger.debug(
            f"...move this file to {source_dir} or change option 'eencijfer_datafile' in config-file at {CONFIG_FILE}."
        )
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
        logger.critical(
            f"...move this file to {source_dir} or change option 'eindexamen_datafile' in config-file at {CONFIG_FILE}."
        )
    return eindexamen_datafile


def _create_default_config(CONFIG_FILE: Path) -> None:
    """Creates a default config-file.

    Args:
        CONFIG_FILE (Path): Path to config-file.

    Returns:
        None: writes out a file.
    """
    default_assets_dir = Path.home() / __app_name__ / "assets"
    default_result_dir = Path.home() / __app_name__ / "result"
    default_source_dir = Path.home() / __app_name__ / "eencijfer"
    default_import_definitions_dir = PACKAGE_PROVIDED_IMPORT_DEFINTIONS_DIR

    config = configparser.ConfigParser()

    try:
        config.read(CONFIG_FILE)
        if not config.has_section('default'):
            config.add_section('default')
        source_dir = config.getpath('default', 'source_dir', fallback=default_source_dir.as_posix())
        result_dir = config.getpath('default', 'result_dir', fallback=default_result_dir.as_posix())
        assets_dir = config.getpath('default', 'assets_dir', fallback=default_assets_dir.as_posix())
        import_definitions_dir = config.getpath(
            'default', 'import_definitions_dir', fallback=default_import_definitions_dir.as_posix()
        )

    except Exception as e:
        logger.debug(f"{e}")
        logger.debug("Despite error, adding default-section to config-object...")
        config.add_section('default')

    config.set('default', 'source_dir', source_dir.as_posix())

    eencijfer_files = _get_list_of_eencijfer_files_in_dir(config)
    if not eencijfer_files:
        typer.echo(f"No eencijfer-files found at {source_dir}. Move them or...")
        typer.echo(f"...edit the config-file at {CONFIG_FILE}")

    config.set('default', 'result_dir', result_dir.as_posix())
    config.set('default', 'assets_dir', assets_dir.as_posix())

    config.set("default", "import_definitions_dir", import_definitions_dir.as_posix())

    config.set("default", "label_naming_style", "PascalCase")
    config.set("default", "table_naming_style", "original")

    with open(CONFIG_FILE, "w") as configfile:  # save
        config.write(configfile)

    return None
