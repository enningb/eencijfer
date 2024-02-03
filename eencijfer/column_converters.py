"""Converters for columns on read-time."""
import numpy as np
import pandas as pd

from eencijfer import column_converter


@column_converter
def convert_to_object(x: pd.Series) -> pd.Series:
    """Convert column to string.

    Args:
        x (pd.Series): column

    Returns:
        pd.Series: all values will be string
    """
    return str(x)


@column_converter
def convert_to_int64(x):
    """Convert column to int64.

    Args:
        x (pd.Series): column

    Returns:
        pd.Series: all values will be int64
    """
    return int(x)


@column_converter
def convert_to_float64(x):
    """Convert column to float64.

    Args:
        x (pd.Series): column

    Returns:
        pd.Series: all values will be float64
    """
    return float(x)


@column_converter
def convert_to_date(x):
    """Convert column to date.

    Args:
        x (pd.Series): column

    Returns:
        pd.Series: all values will be dates.
    """
    return pd.to_datetime(x, format="%Y%m%d")


@column_converter
def convert_to_none(x):
    """Convert column to None.

    Args:
        x (pd.Series): column

    Returns:
        pd.Series: all values will be None
    """
    return None


@column_converter
def convert_geslacht(x):
    """Convert column to readable geslacht (man, vrouw)

    Args:
        x (pd.Series): column

    Returns:
        pd.Series: all values will be man or vrouw
    """
    if x == "M":
        return "man"
    elif x == "V":
        return "vrouw"
    else:
        return "onbekend"


@column_converter
def convert_opleidingsvorm(x):
    """Converts a value to int and than adds opleidingsvorm as string.

    Args:
        x (pd.Series): column

    Returns:
        pd.Series: all values will be in voltijd, deeltijd, duaal.
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
    """Converts all values to int, except 0. These will be Nan.

    Args:
        x (pd.Series): column

    Returns:
        pd.Series: all values will int or Nan.
    """
    if int(x) == 0:
        return np.nan
    else:
        return int(x)
