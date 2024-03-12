"""Top-level package for eencijfer."""

__author__ = """Bram Enning"""
__email__ = 'bramenning@gmail.com'
__version__ = '2024.2.0'
__app_name__ = 'eencijfer'

import logging
import shutil
from importlib import import_module
from pathlib import Path

logger = logging.getLogger(__name__)

APP_NAME = __app_name__
DOT_APP_NAME = '.' + APP_NAME

# create config directory if it does not exist.
APP_DIR = Path.home() / DOT_APP_NAME
Path(APP_DIR).mkdir(parents=True, exist_ok=True)

CONFIG_FILE = APP_DIR / "config.INI"


# default directory for import_definitions if it does not exist.
# DEFAULT_IMPORT_DEFINITIONS_DIR = APP_DIR / 'import_definitions'


# # Source path with all definition files
here = Path(__file__).parent.absolute()
PACKAGE_PROVIDED_IMPORT_DEFINTIONS_DIR = here / "import_definitions"

# try:
#     shutil.copytree(PACKAGE_PROVIDED_IMPORT_DEFINTIONS_DIR, DEFAULT_IMPORT_DEFINITIONS_DIR)
#     logger.debug(f"Files copied successfully to {DEFAULT_IMPORT_DEFINITIONS_DIR}.")
# except FileExistsError:
#     logger.debug(f'Directory {DEFAULT_IMPORT_DEFINITIONS_DIR} already exists!')
#     logger.debug('It will be untouched.')
#     logger.debug(f'If you want the default definitions, remove {DEFAULT_IMPORT_DEFINITIONS_DIR}.')


CONVERTERS = {}


def column_converter(func):
    """Adds column-converter to a dictionary.

    Args:
        func (function): Simple function that converts values in a pandas column.

    Returns:
        func: _description_
    """
    name = func.__name__
    CONVERTERS[name] = func
    return func


# import module so all column-converter-decorators are activated
import_module("eencijfer.column_converters")


FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

logging.basicConfig(format=FORMAT, level=logging.INFO)
