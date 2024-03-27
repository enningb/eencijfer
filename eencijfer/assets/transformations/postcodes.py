"""Add postcodes and gemeente."""

import logging
from pathlib import Path

import pandas as pd

from eencijfer.settings import config

HERE = Path(__file__).parent.absolute()
DATASETS_DIR = HERE / "datasets"
logger = logging.getLogger(__name__)


def _add_isced(eencijfer: pd.DataFrame) -> pd.DataFrame:
    """Add columns with ISCED-codes.

    Args:
        eencijfer (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    logger.debug("Check whether Dec_ho_ISCED has Opleidingscode as index.")
    source_dir = config.getpath('default', 'source_dir')
    Dec_ho_ISCED = pd.read_parquet(source_dir / 'Dec_ho_ISCED.parquet')

    if not len(Dec_ho_ISCED) == Dec_ho_ISCED.Opleidingscode.nunique():
        raise Exception('Something went, Opleidingscode is not unique.')

    logger.debug("Merge eencijfer with Dec_ho_ISCED")
    result = pd.merge(
        eencijfer,
        Dec_ho_ISCED,
        left_on="Opleidingscode",
        right_on="Opleidingscode",
        how="left",
        suffixes=["", "_opleiding"],
    )

    if not result.ISCEDF2013Rubriek.isnull().sum() == 0:
        raise Exception("Not all rows have ISCEDF2013Rubriek")

    new_cols = set(result.columns) - set(eencijfer.columns)
    if len(new_cols) == 0:
        raise Exception("Merge did not give new columns.")

    logger.info("Following columns were added:")
    for col in new_cols:
        logger.info(f" - {col}")

    return result
