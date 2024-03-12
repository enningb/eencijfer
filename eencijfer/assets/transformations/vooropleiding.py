"""Vooropleiding and InstellingVooropleiding."""

import logging

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

    if "mbo" in string:
        return "mbo"
    elif "vwo" in string:
        return "vwo"
    elif "havo" in string:
        return "havo"
    elif "hbo-p" in string:
        return "hbo-p"
    elif "hbo-ba" in string:
        return "hbo-ba"
    elif "hbo-ad" in string:
        return "hbo-ad"
    elif "wo-ba" in string:
        return "wo-ba"
    elif "wo-on/ma" or "wo-pim" in string:
        return "wo-master"
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
        "200": "ONB",
        "201": "ALG",
        "202": "CM",
        "203": "EM",
        "204": "EM & CM",
        "205": "NG",
        "206": "NG & CM",
        "207": "NG & EM",
        "208": "NT",
        "209": "NT & CM",
        "210": "NT & EM",
        "211": "NT & NG",
        "400": "ONG",
        "401": "ALG",
        "402": "CM",
        "403": "EM",
        "404": "EM & CM",
        "405": "NG",
        "406": "NG & CM",
        "407": "NG & EM",
        "408": "NT",
        "409": "NT & CM",
        "410": "NT & EM",
        "411": "NT & NG",
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

    result_path = config.getpath('default', 'result_dir')
    Dec_vopl = pd.read_parquet(result_path / 'Dec_vopl.parquet')
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
    result_path = config.getpath('default', 'result_dir')
    Dec_vooropl = pd.read_parquet(result_path / 'Dec_vooropl.parquet')

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


def _add_naam_instelling_vooropleiding(eencijfer: pd.DataFrame, vooropleiding: str = 'HoogsteVooroplVoorHetHo') -> pd.DataFrame:
    """Add name of institution that provided vooropleiding.

    Args:
        eencijfer (pd.DataFrame): _description_
        config (configparser.ConfigParser, optional): _description_. Defaults to config.
        vooropleiding (str, optional): _description_. Defaults to 'HoogsteVooroplVoorHetHo'.

    Returns:
        pd.DataFrame: _description_
    """
    result_path = config.getpath('default', 'result_dir')
    Dec_brinvestigingsnummer = pd.read_parquet(result_path / 'Dec_brinvestigingsnummer.parquet')

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
