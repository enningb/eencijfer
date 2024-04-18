"""Functions needed for writing to db."""

import logging
from pathlib import Path

import duckdb

from eencijfer.utils.detect_eencijfer_files import (
    _get_eencijfer_datafile,
    _get_eindexamen_datafile,
    _get_list_of_eencijfer_files_in_dir,
)

logger = logging.getLogger(__name__)


def _create_duckdb(source_dir: Path, result_dir: Path, db_name: str) -> None:
    """Create a duckdb-db and load parquet-files.

    Args:
        source_dir (Path): _description_
        result_dir (Path): _description_
        db_name (str): _description_

    Returns:
        _type_: _description_
    """

    eencijfer_files = _get_list_of_eencijfer_files_in_dir(source_dir)
    eencijfer_fname = _get_eencijfer_datafile(source_dir=source_dir)
    eindexamen_fname = _get_eindexamen_datafile(source_dir=source_dir)

    duckdb_path: Path = result_dir / db_name
    logger.debug(f'Creating a duckdb at {duckdb_path}')

    if duckdb_path.is_file():
        logger.warning(f'...removing existing duckdb at {duckdb_path}')
        duckdb_path.unlink()

    if eencijfer_files is not None:
        if duckdb_path.is_file():
            logger.warning(f'...removing existing duckdb at {duckdb_path}')
            duckdb_path.unlink()

        _import_parquet_to_duckdb(eencijfer_files=eencijfer_files, duckdb_path=duckdb_path)

    if eencijfer_fname is not None:
        _create_view(duckdb_path=duckdb_path, source_table=eencijfer_fname, view_name='eencijfer')

    if eindexamen_fname is not None:
        _create_view(duckdb_path=duckdb_path, source_table=eindexamen_fname, view_name='eindexamen')

    return None


def _import_parquet_to_duckdb(eencijfer_files: list, duckdb_path: Path) -> None:
    """Imports parquet-files into duckdb.

    Returns:
        None: _description_
    """

    with duckdb.connect(duckdb_path.as_posix()) as con:
        logger.debug(f'Writing to {duckdb_path}')
        for file in eencijfer_files:
            table = (file.stem).replace('-', '_')
            logger.debug(f"...writing {file} to table {table}")
            query = f"""
                CREATE TABLE
                    {table}
                AS
                    SELECT *
                    FROM
                    read_parquet('{file}')"""

            con.execute(query)
    return None


def _create_view(duckdb_path: Path, source_table: str, view_name: str) -> None:
    """Create view for given source_table.

    Returns:
        None: _description_
    """

    with duckdb.connect(duckdb_path.as_posix()) as con:
        logger.debug(f'Creating a view named {view_name} for {source_table}...')
        logger.debug(f'... at {duckdb_path}.')
        query = f"CREATE VIEW {view_name} AS SELECT * from '{source_table}';"
        con.execute(query)
    return None
