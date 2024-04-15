"""Tools to save to files."""

import logging
from enum import Enum
from pathlib import Path

import pandas as pd

from eencijfer.settings import config
from eencijfer.utils.detect_eencijfer_files import _get_list_of_eencijfer_files_in_dir

logger = logging.getLogger(__name__)

result_dir = config.getpath('default', 'result_dir')


class ExportFormat(str, Enum):
    """File format that will be used to convert to.

    Args:
        str (_type_): _description_
        Enum (_type_): _description_
    """

    csv = "csv"
    parquet = "parquet"
    xlsx = "xlsx"


def _save_to_file(
    df: pd.DataFrame,
    dir: Path,
    fname: str,
    export_format: ExportFormat = ExportFormat.parquet,
):
    """Saves data in the export_format in the result-directory.

    Args:
        df (pd.DataFrame): _description_
        fname (str, optional): _description_. Defaults to "unknown".
        export_format (ExportFormat, optional): _description_. Defaults to ExportFormat.parquet.
        config (configparser.ConfigParser, optional): _description_. Defaults to config.

    Returns:
        None: None
    """

    fpath = Path(dir / fname)

    if export_format.value == 'csv':
        target_fpath = Path(fpath).with_suffix('.csv')
        logger.info(f"Saving {fname} to {target_fpath}...")
        df.to_csv(target_fpath, sep=",", index=False)

    if export_format.value == 'parquet':
        target_fpath = Path(fpath).with_suffix('.parquet')
        logger.info(f"Saving {fname} to {target_fpath}...")
        df.to_parquet(target_fpath)

    if export_format.value == 'xlsx':
        target_fpath = Path(fpath).with_suffix('.xlsx')
        logger.info(f"Saving {fname} to {target_fpath}...")
        df.to_excel(target_fpath, index=False)

    return None


def _convert_to_export_format(source_dir: Path, result_dir: Path, export_format: ExportFormat = ExportFormat.parquet):
    """Convert files in directory to exportformat.

    Args:
        source_dir (Path): Path to directory with parquet files. Defaults to None.
        result_dir (Path): Path to directory with files in export-format. Defaults to None.
        export_format (ExportFormat, optional): _description_. Defaults to ExportFormat.parquet.

    Returns:
        None: None
    """
    eencijfer_files = _get_list_of_eencijfer_files_in_dir(source_dir)

    if eencijfer_files is None:
        raise Exception('No eencijfer-files found!')

    for file in eencijfer_files:
        target_fpath = Path(result_dir / file.name).with_suffix(f".{export_format.value}")

        logger.info("**************************************")
        logger.info("**************************************")
        logger.info("")
        logger.info(f"   Start reading: {file.name}")
        logger.info("")
        logger.info(f"   source_file:{file}")
        logger.info(f"   target_fpath:{target_fpath}")
        logger.info("")
        logger.info("")

        try:
            raw_data = pd.read_parquet(file)

            if len(raw_data) > 0:
                logger.debug(f"...reading {file.name} succeeded.")
                logger.debug(f"...saving to {target_fpath}.")
                _save_to_file(raw_data, dir=result_dir, fname=file.stem, export_format=export_format)

            else:
                logger.info(f"...there does not seem to be data in {file.name}!")
        except Exception as e:
            logger.warning(f"...inlezen van {file.name} mislukt.")
            logger.warning(f"{e}")

        logger.info("**************************************")
    return None
