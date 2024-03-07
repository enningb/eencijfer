"""All functions regarding opleiding."""

import configparser
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from eencijfer.settings import config

HERE = Path(__file__).parent.absolute()
DATASETS_DIR = HERE / "datasets"
logger = logging.getLogger(__name__)


def _add_naam_opleiding(eencijfer: pd.DataFrame, config: configparser.ConfigParser = config) -> pd.DataFrame:
    """Add column with Croho-name.

    Args:
        eencijfer (pd.DataFrame): _description_
        config (configparser.ConfigParser, optional): _description_. Defaults to config.

    Returns:
        pd.DataFrame: _description_
    """
    logger.debug("Controleer of Dec_isat maar 1 naam per Croho bevat.")
    result_path = config.getpath('default', 'result_dir')
    Dec_isat = pd.read_parquet(result_path / 'Dec_isat.parquet')

    if not len(Dec_isat) == Dec_isat.Opleidingscode.nunique():
        raise Exception('Something went, Isat is not unique.')

    logger.debug("Merge eencijfer met Dec_isat")
    result = pd.merge(
        eencijfer,
        Dec_isat,
        left_on="OpleidingActueelEquivalent",
        right_on="Opleidingscode",
        how="left",
        suffixes=["", "_opleiding"],
    )

    logger.debug("Controleer het resultaat...")
    logger.debug("... geen missende namen")
    if not result.NaamOpleiding.isnull().sum() == 0:
        raise Exception("Niet alle opleidingen hebben een naam")

    if result.NaamOpleiding.isnull().sum() > 0:
        opleidingen_zonder_naam = result[result.NaamOpleiding.isnull()][
            [
                "OpleidingActueelEquivalent",
            ]
        ].drop_duplicates()

        logger.info("Er zijn opleidingen zonder naam:")
        logger.info(f"{opleidingen_zonder_naam}")
        logger.info("Missende waarden worden op 'onbekend' gezet.")
        result.NaamOpleiding.fillna("onbekend", inplace=True)

    logger.info("Hernoem NaamOpleiding naar NaamOpleidingCroho")
    result.rename(columns={"NaamOpleiding": "NaamOpleidingCroho"}, inplace=True)

    removable_cols = [col for col in result.columns if "_opleiding" in col]
    for col in removable_cols:
        del result[col]

    nieuwe_cols = set(result.columns) - set(eencijfer.columns)
    logger.info("De volgende kolommen zijn toegevoegd:")
    logger.info(f"{nieuwe_cols}")
    return result


def _add_lokale_naam_opleiding_faculteit(eencijfer: pd.DataFrame) -> pd.DataFrame:
    """Add local names for opleiding.

    Args:
        eencijfer (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: Eencijfer with columns added.
    """
    lokale_namen_fpath = DATASETS_DIR / "21RI" / "croho_naam_opleiding_faculteit.csv"

    if not lokale_namen_fpath.exists():
        raise Exception(f"Bestand {lokale_namen_fpath} bestaat niet!")

    lokale_namen = pd.read_csv(lokale_namen_fpath, sep=";", dtype="object")

    result = pd.merge(
        eencijfer,
        lokale_namen,
        left_on="OpleidingActueelEquivalent",
        right_on="Opleidingscode",
        how="left",
        suffixes=["", "_naam"],
    )
    if "Opleidingscode_naam" in result:
        del result["Opleidingscode_naam"]
    if not len(eencijfer) == len(result):
        raise Exception("Something went wrong merging.")
    if result.CodeOpleiding.isnull().sum() > 0:
        logger.info("Er zijn opleidingen zonder lokale naam:")
        opleidingen_zonder_lokale_naam = result[result.CodeOpleiding.isnull()][
            ["OpleidingActueelEquivalent", "NaamOpleiding"]
        ].drop_duplicates()
        logger.info(f"{opleidingen_zonder_lokale_naam}")

    nieuwe_cols = set(result.columns) - set(eencijfer.columns)
    logger.info("De volgende kolommen zijn toegevoegd:")
    logger.info(f"{nieuwe_cols}")

    return result


def _add_type_opleiding(eencijfer: pd.DataFrame) -> pd.DataFrame:
    """Add column with type opleiding (bachelor, master, et cetera).

    Args:
        eencijfer (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: Eencijfer with added column.
    """
    result = eencijfer.copy()

    typeOpleiding = {
        "O": "oude stijl (toegestaan t/m studiejaar 1992-1993)",
        "P": "propedeuse",
        "1": "1e fase (WO); hoofdfase (HBO) (toegestaan t/m studiejaar 92-93)",
        "2": "2e fase (toegestaan t/m studiejaar 1996-1997)",
        "I": "initiële opleiding (toegestaan vanaf studiejaar 1993-1994)",
        "V": "vervolgopleiding (toegestaan vanaf studiejaar 1993-1994)",
        "K": "kandidaatsfase",
        "D": "propedeuse bachelor",
        "B": "bachelor",
        "M": "master",
        "A": "associate degree",
        "T": "tussentijds doctoraal",
        "Q": "post-initiële master",
    }
    logger.debug("...voeg TypeOpleiding toe op basis van Opleidingsfase")
    result["TypeOpleiding"] = result.Opleidingsfase.replace(typeOpleiding)
    result["TypeOpleiding"] = result["TypeOpleiding"].fillna("onbekend")

    nieuwe_cols = set(result.columns) - set(eencijfer.columns)
    logger.info("De volgende kolommen zijn toegevoegd:")
    logger.info(f"{nieuwe_cols}")

    return result


def _add_opleiding(eencijfer: pd.DataFrame) -> pd.DataFrame:
    """Adds column opleiding with most recent Croho.

    Args:
        eencijfer (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: eencijfer with column added.
    """
    eencijfer["opleiding"] = np.where(
        eencijfer.OpleidingHistorischEquivalent.notnull(),
        eencijfer.OpleidingHistorischEquivalent,
        eencijfer.OpleidingActueelEquivalent,
    )
    return eencijfer


def _add_croho_onderdeel(eencijfer: pd.DataFrame) -> pd.DataFrame:
    """Adds column with CrohoOnderdeel (natuur, economie, et cetera).

    Args:
        eencijfer (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: Eencijfer with column added.
    """
    if "CrohoOnderdeelActueleOpleiding" not in eencijfer:
        raise Exception("CrohoOnderdeelActueleOpleiding niet gevonden in dataset")

    result = eencijfer.copy()

    croho_sectoren = {
        1: "onderwijs",
        2: "landbouw en natuurlijke omgeving",
        3: "natuur",
        4: "techniek",
        5: "gezondheidszorg",
        6: "economie",
        7: "recht",
        8: "gedrag en maatschappij",
        9: "taal en cultuur",
        0: "sectoroverstijgend",
    }
    logger.debug("...voeg CrohoOnderdeel toe op basis van CrohoOnderdeelActueleOpleiding")
    result["CrohoOnderdeel"] = result.CrohoOnderdeelActueleOpleiding.replace(croho_sectoren).fillna("onbekend")

    return result
