"""Settings for eencijfer."""

import configparser
import logging
from pathlib import Path

from eencijfer import CONFIG_FILE, PACKAGE_PROVIDED_IMPORT_DEFINTIONS_DIR

logger = logging.getLogger(__name__)

default_source_dir = Path().absolute()
default_assets_dir = default_source_dir / "assets"
default_result_dir = default_source_dir / "result"
default_import_definitions_dir = PACKAGE_PROVIDED_IMPORT_DEFINTIONS_DIR


def _get_config(
    CONFIG_FILE: Path,
    result_dir: Path = default_result_dir,
    source_dir: Path = default_source_dir,
    assets_dir: Path = default_assets_dir,
    import_definitions_dir: Path = default_import_definitions_dir,
    use_column_converter: bool = False,
    remove_pii: bool = True,
) -> configparser.ConfigParser:
    config = configparser.ConfigParser(converters={"path": lambda x: Path(x), "list": lambda x: x.split(',')})

    try:
        if CONFIG_FILE.is_file():
            config.read(CONFIG_FILE)
        if not config.has_section('default'):
            config.add_section('default')
        if not config.has_option('default', 'source_dir'):
            config.set('default', 'source_dir', source_dir.as_posix())
        if not config.has_option('default', 'result_dir'):
            config.set('default', 'result_dir', result_dir.as_posix())
        if not config.has_option('default', 'assets_dir'):
            config.set('default', 'assets_dir', assets_dir.as_posix())
        if not config.has_option('default', 'import_definitions_dir'):
            config.set('default', 'import_definitions_dir', import_definitions_dir.as_posix())
        if not config.has_option('default', 'use_column_converter'):
            config.set('default', 'use_column_converter', str(use_column_converter))
        if not config.has_option('default', 'remove_pii'):
            config.set('default', 'remove_pii', str(remove_pii))

    except Exception as e:
        logger.debug(f"{e}")
        logger.debug("Something went wrong reading config file...")

    return config


config = _get_config(CONFIG_FILE)
