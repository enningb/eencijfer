"""Prestatieafspraken code."""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _add_pa_cohort(eencijfer: pd.DataFrame) -> pd.DataFrame:
    """Add an indicator whether row belongs to pa-cohort.

    Args:
        eencijfer (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: Eencijfer with column indicating whether row is part of PA-cohort.
    """
    # Voeg een hulpkolom toe:
    logger.debug('Add column Aantal')
    eencijfer["Aantal"] = 1
    # Filter: actief op 1 oktober
    filter_actiefopPeildatum = eencijfer.IndicatieActiefOpPeildatum == 1

    # Hoofdinschrijving
    # srt_inschr_typeho: Soort inschrijving type ho binnen soort ho
    filter_soortinschrijving_ho = eencijfer.SoortInschrijvingHogerOnderwijs == 1
    # Bacheloropleiding
    filter_type_ho = eencijfer.TypeHogerOnderwijsBinnenSoortHogerOnderwijs == "ba"
    # Geen AD
    filter_opleidingscode = np.invert(eencijfer.Opleidingscode.astype(str).str.startswith("80"))
    # Voltijd
    filter_voltijd = eencijfer.Opleidingsvorm == "voltijd"
    # Direct na vooropleiding ingestroomd in ho
    filter_hoogstevooropleiding = eencijfer.HoogsteVooropleiding == eencijfer.HoogsteVooropleidingVoorHetHo
    # Eerste jaar in HO
    filter_eerstejaar_in_ho = eencijfer.EersteJaarInHetHogerOnderwijs == eencijfer.Inschrijvingsjaar

    logger.debug('Add InPACohortDefinitie.')
    eencijfer["InPACohortDefinitie"] = np.where(
        (filter_actiefopPeildatum)
        & (filter_soortinschrijving_ho)
        & (filter_type_ho)
        & (filter_opleidingscode)
        & (filter_voltijd)
        & (filter_hoogstevooropleiding)
        & (filter_eerstejaar_in_ho),
        "Ja",
        "Nee",
    )

    return eencijfer
