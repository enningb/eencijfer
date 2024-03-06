"""Code for eindexamencijfers."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from eencijfer.assets.transformations.vooropleiding import _add_oorspronkelijke_vooropleiding, _add_vooropleiding_kort
from eencijfer.init import _get_eindexamen_datafile
from eencijfer.settings import config

logger = logging.getLogger(__name__)


def _create_eindexamencijfer_df() -> pd.DataFrame:
    result_path = Path(config.get('default', 'result_dir'))

    eindexamencijfers_fname = _get_eindexamen_datafile(result_path)
    eindexamencijfers = pd.read_parquet(Path(result_path / eindexamencijfers_fname).with_suffix('.parquet'))
    eindexamencijfers = _add_oorspronkelijke_vooropleiding(eindexamencijfers)
    eindexamencijfers = _add_vooropleiding_kort(
        eindexamencijfers,
        source_column="OmschrijvingVooropleidingOorspronkelijkeCode",
        new_column="Vooropleiding",
    )

    fields = [
        "PersoonsgebondenNummer",
        "Diplomajaar",
        "VakCode",
        "VakAfkorting",
        "Vooropleiding",
        "CijferEersteCentraalExamen",
        "CijferTweedeCentraalExamen",
        "CijferDerdeCentraalExamen",
        "CijferSchoolexamen",
    ]
    logger.debug(f"filter op kolommen:")
    logger.debug(f"")
    logger.debug(f"{fields}")

    logger.debug(f"...melt...")
    result = pd.melt(
        eindexamencijfers[fields],
        id_vars=[
            "PersoonsgebondenNummer",
            "Vooropleiding",
            "Diplomajaar",
            "VakCode",
            "VakAfkorting",
        ],
    )
    logger.debug(f"...lege waarden weghalen...")
    result = result.dropna(subset=["value"])

    result["Poging"] = np.where(result.variable.str.contains("Eerste"), 1, np.nan)
    result["Poging"] = np.where(result.variable.str.contains("Tweede"), 2, result["Poging"])
    result["Poging"] = np.where(result.variable.str.contains("Derde"), 3, result["Poging"])
    result["Poging"] = result["Poging"].fillna(1)

    result["SoortExamen"] = np.where(result.variable.str.contains("Centraal"), "CSE", "School")

    # sorteer de pogingen van hoog naar laag, dan ontdubbelen en de eerste waarde (de laatste poging dus)
    # vasthouden.
    laatste_cijfer = result.sort_values(
        by=[
            "PersoonsgebondenNummer",
            "Vooropleiding",
            "SoortExamen",
            "VakAfkorting",
            "VakCode",
            "Poging",
        ],
        ascending=False,
    ).drop_duplicates(
        subset=[
            "PersoonsgebondenNummer",
            "Vooropleiding",
            "SoortExamen",
            "VakAfkorting",
            "VakCode",
        ],
        keep="first",
        ignore_index=True,
    )

    laatste_cijfer.rename(columns={"value": "Cijfer"}, inplace=True)

    if "variable" in laatste_cijfer:
        del laatste_cijfer["variable"]

    return laatste_cijfer
