"""Top-level package for eencijfer."""

__author__ = """Bram Enning"""
__email__ = 'bramenning@gmail.com'
__version__ = '0.2.18'


import logging
from pathlib import Path

logger = logging.getLogger(__name__)

APP_NAME = 'eencijfer'
DOT_APP_NAME = '.' + APP_NAME
APP_DIR = Path.home() / DOT_APP_NAME
# create config directory if it does not exist.

Path(APP_DIR).mkdir(parents=True, exist_ok=True)

CONFIG_FILE = APP_DIR / "config.INI"

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

logging.basicConfig(format=FORMAT, level=logging.INFO)
