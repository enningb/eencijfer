"""All functions regarding diploma."""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _add_ho_diploma_eerstejaar(eencijfer: pd.DataFrame) -> pd.DataFrame:
    """Add column indicating ho-diploma in first year.

    Args:
        eencijfer (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """

    # Indicator voor die studenten die in het 1e jaar een diploma halen, die wordt later weer weggefilterd:
    eencijfer["HoDiplomaInEersteJaar"] = np.where(
        (
            (eencijfer.SoortDiplomaSoortHogerOnderwijs >= 3)
            & (eencijfer.SoortDiplomaSoortHogerOnderwijs <= 10)
            & (eencijfer.Diplomajaar == eencijfer.EersteJaarAanDezeActueleInstelling)
        ),
        1,
        0,
    )
    return eencijfer


def _add_soort_diploma(eencijfer: pd.DataFrame) -> pd.DataFrame:
    """Add column SoortDiploma with pretty description.

    Args:
        eencijfer (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    if "OpleidingsfaseActueelVanHetDiploma" not in eencijfer:
        raise Exception("OpleidingsfaseActueelVanHetDiploma mist in eencijfer")

    logger.info("Toevoegen SoortDiploma...")
    soort_diploma = {
        "D": "propedeuse",
        "A": "associate degree",
        "B": "bachelor",
        "M": "master",
        "Q": "post-initiele master",
    }

    logger.debug("...voeg SoortDiploma toe op basis van OpleidingsfaseActueelVanHetDiploma")

    eencijfer["SoortDiploma"] = eencijfer.OpleidingsfaseActueelVanHetDiploma.replace(soort_diploma)

    return eencijfer
