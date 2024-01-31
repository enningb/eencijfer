import numpy as np
import pandas as pd

from eencijfer import column_converter


@column_converter
def convert_to_object(x: pd.Series) -> pd.Series:
    return str(x)


@column_converter
def convert_to_int64(x):
    return int(x)


@column_converter
def convert_to_float64(x):
    return float(x)


@column_converter
def convert_to_date(x):
    """Zet x om naar een datumveld"""
    return pd.to_datetime(x, format="%Y%m%d")


@column_converter
def convert_to_none(x):
    """Zet x om naar een leeg veld"""
    return None


@column_converter
def convert_geslacht(x):
    """Zet x om naar een leesbare geslachtsomschrijving"""
    if x == "M":
        return "man"
    elif x == "V":
        return "vrouw"
    else:
        return "onbekend"


@column_converter
def convert_opleidingsvorm(x):
    """Converts a value to int and than adda Opleidingsvorm as string.
    :param x:
    :return: a string
    """

    if int(x) == 1:
        return "voltijd"
    elif int(x) == 2:
        return "deeltijd"
    elif int(x) == 3:
        return "duaal"
    else:
        return x


@column_converter
def convert_to_int_zero_to_nan(x):
    """converts a 0 to NaN"""
    if int(x) == 0:
        return np.nan
    else:
        return int(x)
