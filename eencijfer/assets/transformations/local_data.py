"""Add local, institution specific, data."""

import logging

import pandas as pd

from eencijfer.settings import config

logger = logging.getLogger(__name__)


def _add_local_id(data: pd.DataFrame) -> pd.DataFrame:
    """Adds a local id (e.g. studentnummer).

    Args:
        data (pd.DataFrame): df with PersoonsgebondenNummer.

    Raises:
        Exception: Merge error.

    Returns:
        pd.DataFrame: data with local-id added.
    """

    logger.info('Adding local_ids.')
    fpath = config.getpath('local_id', 'fpath')
    left_on = config.get('local_id', 'left_on')
    right_on = config.get('local_id', 'right_on')
    how = config.get('local_id', 'how')
    logger.info(f'... merging {left_on} with {right_on} for local_ids.')

    local_ids = pd.read_parquet(fpath)
    result = pd.merge(data, local_ids, left_on=left_on, right_on=right_on, how='left')
    if (how == 'left') and (len(data) != len(result)):
        raise Exception('Merge went wrong!')

    return result
