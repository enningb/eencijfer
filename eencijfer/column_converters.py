"""Converters for columns on read-time."""

import numpy as np
import pandas as pd

from eencijfer import column_converter


@column_converter
def convert_to_object(x) -> str:
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
    """Convert column to readable geslacht (man, vrouw).

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
    """Converts an integer code to its corresponding educational form.

    This function takes an integer 'x' representing an educational form code and returns
    the corresponding educational form as a string.

    Args:
        x (int): An integer representing the educational form code.

    Returns:
        str: The corresponding educational form as a string ('voltijd', 'deeltijd', 'duaal').

    Example:
        >>> convert_opleidingsvorm(1)
        'voltijd'
        >>> convert_opleidingsvorm(2)
        'deeltijd'
        >>> convert_opleidingsvorm(3)
        'duaal'
        >>> convert_opleidingsvorm(4)
        4  # Returns the input 'x' as is for unknown codes.
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
