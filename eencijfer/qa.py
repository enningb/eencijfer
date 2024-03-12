"""Convenience functions for quality assurance."""

import configparser
from pathlib import Path
from typing import Optional

import pandas as pd

from eencijfer.eencijfer import _get_list_of_eencijfer_files_in_dir, _match_file_to_definition
from eencijfer.settings import config


def _get_definition(row: pd.Series, col_name: str = 'path') -> Optional[Path]:
    """Gives definition-file for path (if it exists, otherwise None).

    Args:
        row (pd.Series): A series with field 'path'.

    Returns:
        Optional[Path]: _description_
    """
    definition = _match_file_to_definition(row[col_name])
    return definition


def compare_eencijfer_files_and_definitions(config: configparser.ConfigParser = config) -> pd.DataFrame:
    """Compare definition files and eencijfer files.

    Args:
        config (configparser.ConfigParser, optional): _description_. Defaults to config.

    Returns:
        pd.DataFrame: prints out df.
    """
    eencijfer_fpaths = _get_list_of_eencijfer_files_in_dir()
    if eencijfer_fpaths is not None:
        eencijfer_files: list = [f.stem for f in eencijfer_fpaths]
    eencijfer_df: pd.DataFrame = pd.DataFrame({'eencijfer_file': eencijfer_files, 'path': eencijfer_fpaths})

    eencijfer_df['definition'] = eencijfer_df.apply(_get_definition, axis=1)

    definition_dir = config.getpath('default', 'import_definitions_dir')
    definition_fpaths = [p for p in definition_dir.iterdir() if p.suffix in [".csv"]]
    definition_files = [f.stem for f in definition_fpaths]
    definition_df = pd.DataFrame({'eencijfer_file': definition_files, 'definition': definition_fpaths})

    definition_without_eencijfer = definition_df[~definition_df.definition.isin(eencijfer_df.definition.tolist())].copy()

    result = pd.concat([eencijfer_df, definition_without_eencijfer]).fillna('❌')

    return result
