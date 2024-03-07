"""Eencijfer data asset."""

import logging
from pathlib import Path

import pandas as pd

from eencijfer.assets.transformations.diploma import _add_ho_diploma_eerstejaar, _add_soort_diploma
from eencijfer.assets.transformations.opleiding import (
    _add_croho_onderdeel,
    _add_lokale_naam_opleiding_faculteit,
    _add_naam_opleiding,
    _add_opleiding,
    _add_type_opleiding,
)
from eencijfer.assets.transformations.prestatieafspraken import _add_pa_cohort
from eencijfer.assets.transformations.vooropleiding import _add_naam_instelling_vooropleiding, _add_vooropleiding
from eencijfer.init import _get_eencijfer_datafile
from eencijfer.settings import config

logger = logging.getLogger(__name__)


def _create_eencijfer_df():
    """Pipeline voor verrijken van eencijfer-basisbestand."""

    result_path = config.getpath('default', 'result_dir')

    eencijfer_fname = _get_eencijfer_datafile(result_path)
    eencijfer = pd.read_parquet(Path(result_path / eencijfer_fname).with_suffix('.parquet'))

    eencijfer["Aantal"] = 1

    # voeg informatie over vooropleiding toe:
    eencijfer = _add_vooropleiding(eencijfer, vooropleiding_field="HoogsteVooropleiding")

    eencijfer = _add_naam_instelling_vooropleiding(
        eencijfer,
        vooropleiding="HoogsteVooropleiding",
    )
    # voeg informatie over inschrijving toe:
    eencijfer = _add_naam_opleiding(eencijfer)
    eencijfer = _add_opleiding(eencijfer)
    eencijfer = _add_croho_onderdeel(eencijfer)
    eencijfer = _add_soort_diploma(eencijfer)
    eencijfer = _add_ho_diploma_eerstejaar(eencijfer)
    eencijfer = _add_type_opleiding(eencijfer)
    eencijfer = _add_lokale_naam_opleiding_faculteit(eencijfer)
    eencijfer = _add_pa_cohort(eencijfer)

    return eencijfer
