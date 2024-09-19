"""Vooropleiding and InstellingVooropleiding."""

import logging
import re

import pandas as pd

from eencijfer.settings import config

logger = logging.getLogger(__name__)

# In het eencijfer zitten 3 velden die betrekking hebben op de vooropleiding:
# het gaat om:
# 1. HoogsteVooropleiding: hoogste vooropleiding
# 2. HoogsteVooropleidingVoorHetHo: voor het ho
# 3. InstellingVanDeHoogsteVooropleidingBinnenHetHo:


def _determine_vooropleiding(string: str) -> str:
    """Short description of vooropleiding.

    Args:
        string (str): _description_

    Returns:
        str: _description_
    """

    string = string.lower()

    # zoek exacte strings middels regular expressions
    if re.search(r'\bmbo\b', string):
        return "mbo"
    elif re.search(r'\bvwo\b', string):
        return "vwo"
    elif re.search(r'\bhavo\b', string):
        return "havo"
    elif re.search(r'\bhbo-p\b', string):
        return "hbo-p"
    elif re.search(r'\bhbo-ba\b', string):
        return "hbo-ba"
    elif re.search(r'\bhbo-ad\b', string):
        return "hbo-ad"
    elif re.search(r'\bhbo-vo/ma\b', string):
        return "hbo-master"
    elif re.search(r'\bhbo-pim\b', string):
        return "hbo-master"
    elif re.search(r'\bwo-p\b', string):
        return "wo-p"
    elif re.search(r'\bwo-ba\b', string):
        return "wo-ba"
    elif re.search(r'\bwo-on/ma\b', string):
        return "wo-master"
    elif re.search(r'\bwo-pim\b', string):
        return "wo-master"
    elif re.search(r'\bwo-vo/ma/bf\b', string):
        return "wo-master"
    elif re.search(r'\bwo-ba\b', string):
        return "wo-ba"
    else:
        return "overig"


def _add_vooropleiding_kort(
    Dec_vopl: pd.DataFrame,
    source_column: str = "OmschrijvingVooropleiding",
    new_column: str = "Vooropleiding",
) -> pd.DataFrame:
    """Add short notation of vooropleiding.

    Args:
        Dec_vopl (pd.DataFrame): _description_
        source_column (str, optional): _description_. Defaults to "OmschrijvingVooropleiding".
        new_column (str, optional): _description_. Defaults to "Vooropleiding".

    Returns:
        pd.DataFrame: _description_
    """
    logger.info("...voeg korte omschrijving vooropleiding toe (mbo, vwo, etc)")
    Dec_vopl[new_column] = Dec_vopl[source_column].apply(_determine_vooropleiding)
    return Dec_vopl


def _add_profiel_havo_vwo(Dec_vopl: pd.DataFrame) -> pd.DataFrame:
    """Add profiel of havo or vwo vooropleiding.

    Args:
        Dec_vopl (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    profielen = {
        "00200": "ONB",
        "00201": "ALG",
        "00202": "CM",
        "00203": "EM",
        "00204": "EM & CM",
        "00205": "NG",
        "00206": "NG & CM",
        "00207": "NG & EM",
        "00208": "NT",
        "00209": "NT & CM",
        "00210": "NT & EM",
        "00211": "NT & NG",
        "00400": "ONG",
        "00401": "ALG",
        "00402": "CM",
        "00403": "EM",
        "00404": "EM & CM",
        "00405": "NG",
        "00406": "NG & CM",
        "00407": "NG & EM",
        "00408": "NT",
        "00409": "NT & CM",
        "00410": "NT & EM",
        "00411": "NT & NG",
    }
    profielen_df = (
        pd.DataFrame.from_dict(profielen, orient="index")
        .reset_index()
        .rename(columns={"index": "VooropleidingCode", 0: "ProfielVooropleiding"})
    )

    vooropleiding = pd.merge(
        Dec_vopl,
        profielen_df,
        left_on="VooropleidingCode",
        right_on="VooropleidingCode",
        how="left",
    )
    if len(vooropleiding) != len(Dec_vopl):
        raise Exception('Lengths of dataframes do not match, something went wrong merging.')

    vooropleiding["VooropleidingCode"] = vooropleiding["VooropleidingCode"].astype(str)
    return vooropleiding


def _add_vooropleiding(
    eencijfer: pd.DataFrame,
    vooropleiding_field: str = "HoogsteVooropleiding",
) -> pd.DataFrame:
    """Voegt gegevens over vooropleiding toe.

    Args:
        eencijfer (pd.DataFrame): eencijfer
        Dec_vopl (pd.DataFrame): data met gegevens over vooropleiding

    Returns:
        pd.DataFrame: eencijfer verrijkt met vooropleiding (profiel en verkorte notatie)
    """

    source_dir = config.getpath('default', 'source_dir')
    Dec_vopl = pd.read_parquet(source_dir / 'Dec_vopl.parquet')
    vooropleiding = _add_profiel_havo_vwo(Dec_vopl)
    vooropleiding = _add_vooropleiding_kort(vooropleiding)

    result = pd.merge(
        eencijfer,
        vooropleiding,
        left_on=vooropleiding_field,
        right_on="VooropleidingCode",
        how="left",
        suffixes=["", "_Vooropleiding"],
    )
    if not len(result) == len(eencijfer):
        raise Exception("Something went wrong merging.")

    # toekomst: 'VooropleidingKort' bestaat niet, want die heet 'Vooropleiding' (hierin staat de korte omschrijving),
    # maar als je 'Vooropleiding' omzet naar vooropleiding_field, wat 'HoogsteVooropleiding' is
    # krijg je tweemaal een kolom met dezelfde naam, maar andere invulling (codes vs korte beschrijvingen)
    # lijkt me ongewest.
    result.rename(
        columns={
            "OmschrijvingVooropleiding": vooropleiding_field + "Volledig",
            "ProfielVooropleiding": vooropleiding_field + "Profiel",
            "VooropleidingKort": vooropleiding_field,
            "VooropleidingCode": vooropleiding_field + "Code",
        },
        inplace=True,
    )

    # assert len(eencijfer.columns) == len(result.columns) - 3

    return result


def _add_oorspronkelijke_vooropleiding(data: pd.DataFrame) -> pd.DataFrame:
    """Voegt gegevens toe over type vooropleiding aan eindexamencijfers.

    Args:
        data (pd.DataFrame): dataframe met eindexamencijfers.

    Returns:
        pd.DataFrame: dataframe met extra informatie over voorpleiding
    """
    source_dir = config.getpath('default', 'source_dir')
    Dec_vooropl = pd.read_parquet(source_dir / 'Dec_vooropl.parquet')

    result = pd.merge(
        data,
        Dec_vooropl,
        left_on=["VooropleidingOorspronkelijkeCode"],
        right_on=["VooropleidingOorspronkelijkeCode"],
        how="left",
    )
    if len(data) != len(result):
        raise Exception('Lengths of dataframes do not match, something went wrong merging.')
    return result


def _add_naam_instelling_vooropleiding(
    eencijfer: pd.DataFrame, vooropleiding: str = 'HoogsteVooroplVoorHetHo'
) -> pd.DataFrame:
    """Add name of institution that provided vooropleiding.

    Args:
        eencijfer (pd.DataFrame): _description_
        config (configparser.ConfigParser, optional): _description_. Defaults to config.
        vooropleiding (str, optional): _description_. Defaults to 'HoogsteVooroplVoorHetHo'.

    Returns:
        pd.DataFrame: _description_
    """
    source_dir = config.getpath('default', 'source_dir')
    Dec_brinvestigingsnummer = pd.read_parquet(source_dir / 'Dec_brinvestigingsnummer.parquet')

    if vooropleiding not in [
        "HoogsteVooropleiding",
        "HoogsteVooroplVoorHetHo",
        "HoogsteVooroplBinnenHetHo",
    ]:
        raise Exception("Vooropleiding not found in dataframe.")

    brin = "InstellingVanDe" + vooropleiding
    vestiging = "VestigingsnummerVanDe" + vooropleiding

    rename_fields = {
        "Brinnummer": brin,
        "Vestigingsnummer": vestiging,
        "NaamInstellingVooropleiding": "NaamInstelling" + vooropleiding,
        "PostcodeInstellingVooropleiding": "PostcodeInstelling" + vooropleiding,
        "PlaatsInstellingVooropleiding": "PlaatsInstelling" + vooropleiding,
        "DatumOprichtingInstellingVooropleiding": "DatumOprichtingInstelling" + vooropleiding,
        "DatumOpheffingInstellingVooropleiding": "DatumOpheffingInstelling" + vooropleiding,
        "DenominatieInstellingVooropleidingCode": "CodeDenominatieInstelling" + vooropleiding,
        "NaamDenominatieInstellingVooropleiding": "DenominatieInstelling" + vooropleiding,
    }

    instelling_vooropleiding = Dec_brinvestigingsnummer.rename(columns=rename_fields)
    result = pd.merge(
        eencijfer,
        instelling_vooropleiding,
        left_on=[brin, vestiging],
        right_on=[brin, vestiging],
        how="left",
        suffixes=["", "_Vooropleiding"],
    )
    if not len(result) == len(eencijfer):
        raise Exception("Er ging iets mis met mergen...")

    return result
