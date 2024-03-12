"""Tools to save to files."""

import logging
from enum import Enum
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """File format that will be used to convert to.

    Args:
        str (_type_): _description_
        Enum (_type_): _description_
    """

    csv = "csv"
    parquet = "parquet"
    db = "db"


def _save_to_file(
    df: pd.DataFrame,
    dir: Path,
    fname: str,
    export_format: str = 'parquet',
):
    """Saves data in the export_format in the result-directory specified in the config.

    Args:
        df (pd.DataFrame): _description_
        fname (str, optional): _description_. Defaults to "unknown".
        export_format (ExportFormat, optional): _description_. Defaults to ExportFormat.parquet.
        config (configparser.ConfigParser, optional): _description_. Defaults to config.

    Returns:
        None: None
    """

    fpath = Path(dir / fname)

    if export_format == 'csv':
        target_fpath = Path(fpath).with_suffix('.csv')
        logger.info(f"Saving {fname} to {target_fpath}...")
        df.to_csv(target_fpath, sep=",")

    if export_format == 'parquet':
        target_fpath = Path(fpath).with_suffix('.parquet')
        logger.info(f"Saving {fname} to {target_fpath}...")
        df.to_parquet(target_fpath)

    return None
