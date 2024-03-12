"""Tools for removing PII."""

import configparser
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from eencijfer.io.file import _save_to_file
from eencijfer.settings import config
from eencijfer.utils.detect_eencijfer_files import _get_eencijfer_datafile, _get_eindexamen_datafile
from eencijfer.utils.local_data import _add_local_id

logger = logging.getLogger(__name__)

NEW_IDENTIFIER_SUFFIX = "_new"


def _create_pgn_pseudo_id_table(
    data: pd.DataFrame,
    identifier: str = "PersoonsgebondenNummer",
    new_identifier_suffix: str = NEW_IDENTIFIER_SUFFIX,
) -> pd.DataFrame:
    """Creates a table with a random ID based on identifier.

    Args:
        data (pd.DataFrame): Table with identifier.
        identifier (str, optional): . Defaults to "PersoonsgebondenNummer".
        new_identifier_suffix (str, optional): Suffix that's added temporarily. Defaults to NEW_IDENTIFIER_SUFFIX.

    Returns:
        pd.DataFrame: Dataframe with 2 columns: identifier and identifier + suffix
    """

    new_identifier = identifier + new_identifier_suffix
    logger.debug(f"naam new identifier = {new_identifier}")
    if identifier not in data:
        raise Exception(f"Identifier {identifier} does not exist in dataset.")

    koppeltabel = data[
        [
            identifier,
        ]
    ].drop_duplicates()
    if not len(koppeltabel) == data[identifier].nunique():
        raise Exception("Creating table failed...")
    logger.debug("Create identifier by creating  random numbers and fill with 0 until 7 positions.")
    identifier_array = koppeltabel[identifier].tolist()
    koppeltabel[new_identifier] = np.random.permutation(identifier_array)
    koppeltabel[new_identifier] = koppeltabel[new_identifier].astype(str)
    koppeltabel[new_identifier] = koppeltabel[new_identifier].str.zfill(7)
    if not len(koppeltabel) == koppeltabel[new_identifier].nunique():
        raise Exception("New identifier contains duplicates.")
    logger.debug("Create index.")
    koppeltabel = koppeltabel.reset_index()
    del koppeltabel["index"]

    return koppeltabel


def _replace_pgn_with_pseudo_id(
    data: pd.DataFrame,
    koppeltabel: pd.DataFrame,
    identifier: str = "PersoonsgebondenNummer",
    new_identifier_suffix: str = NEW_IDENTIFIER_SUFFIX,
) -> pd.DataFrame:
    """Replace identief with pseudo-id.

    Args:
        data (pd.DataFrame): Table where identifier is to be replaced.
        koppeltabel (pd.DataFrame): table with pseudo-id per id.
        identifier (str, optional): Identifier column. Defaults to "PersoonsgebondenNummer".
        new_identifier_suffix (str, optional): _description_. Defaults to NEW_IDENTIFIER_SUFFIX.

    Returns:
        pd.DataFrame: Table with identifier replaced.
    """

    new_identifier = identifier + new_identifier_suffix
    logger.debug(f"Name new identifier = {new_identifier}")
    logger.debug("Merge koppeltabel aan data")
    result = pd.merge(
        data,
        koppeltabel,
        left_on=identifier,
        right_on=identifier,
        how="left",
    )
    logger.debug("Remove old identifier.")
    del result[identifier]

    logger.debug("Rename new identifier to old identifier.")
    result = result.rename(columns={new_identifier: identifier})
    logger.info('Replaced PersoonsgebondenNummer with a pseudo-id.')
    return result


def _empty_id_fields(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Empty columns with PII.

    Args:
        data (pd.DataFrame): dataframe

    Returns:
        pd.DataFrame: data minus sensitive fields
    """
    sensitive_fields: list = ["Onderwijsnummer", "Burgerservicenummer"]
    logger.debug("Check whether there are fields to be emptied....")
    fields_in_data_to_be_emptied = [field for field in sensitive_fields if field in data]
    if len(fields_in_data_to_be_emptied) > 0:
        for field in fields_in_data_to_be_emptied:
            logger.info(f"Removing all values from column: {field}.")
            data[field] = np.nan
    else:
        logger.info("No columns to be emptied.")

    if len(fields_in_data_to_be_emptied) == 0:
        logger.debug(f"...no column found with names {sensitive_fields}, nothing to be removed.")

    return data


def _replace_all_pgn_with_pseudo_id_remove_pii_local_id(
    config: configparser.ConfigParser = config,
    export_format='parquet',
    remove_pii: bool = True,
    add_local_id: bool = False,
) -> None:
    """Replaces id's with pseudo-id's, removes PII, adds local-'s.

    Args:
        config (configparser.ConfigParser, optional): _description_. Defaults to config.
        export_format (str, optional): Format in which file is saved. Defaults to 'parquet'.

    Returns:
        None: Saves files to result_dir.
    """
    logger.debug('Replacing pgns and removing pii.')
    result_dir = config.getpath('default', 'result_dir')

    eencijfer_fname = _get_eencijfer_datafile(result_dir)
    if eencijfer_fname is None:
        raise Exception("No eencijfer-file found.")
    eencijfer_fpath = Path(result_dir / eencijfer_fname).with_suffix(f'.{export_format}')
    eencijfer = pd.read_parquet(eencijfer_fpath)

    vakken_fname = _get_eindexamen_datafile(result_dir)
    if vakken_fname is None:
        raise Exception("No eindexamen-file found.")

    vakken_fpath = Path(result_dir / vakken_fname).with_suffix(f'.{export_format}')
    vakken = pd.read_parquet(vakken_fpath)

    if add_local_id:
        logger.info('Adding local_id to eencijfer and vakken.')
        eencijfer = _add_local_id(eencijfer)
        vakken = _add_local_id(vakken)

    if remove_pii:
        if add_local_id:
            logger.warning('Not removing local_id! Data still contains PII.')
        logger.info('Creating table with pseudo-ids...')
        koppeltabel = _create_pgn_pseudo_id_table(eencijfer)
        logger.info(f'...removing pgn from {eencijfer_fpath}')
        eencijfer = _replace_pgn_with_pseudo_id(eencijfer, koppeltabel)
        eencijfer = _empty_id_fields(eencijfer)

        logger.info(f'...removing pgn from {vakken_fpath}')
        vakken = _replace_pgn_with_pseudo_id(vakken, koppeltabel)
        vakken = _empty_id_fields(vakken)

    logger.info(f"Saving {eencijfer_fname} to {result_dir}")
    _save_to_file(eencijfer, fname=eencijfer_fname, dir=result_dir, export_format=export_format)

    logger.info(f"Saving {vakken_fname} to {result_dir}")
    _save_to_file(vakken, fname=vakken_fname, dir=result_dir, export_format=export_format)
    return None
