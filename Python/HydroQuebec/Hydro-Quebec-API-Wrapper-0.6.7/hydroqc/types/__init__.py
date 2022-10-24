"""Hydroqc custom types."""
from hydroqc.types.conso import (
    ConsoAnnualTyping,
    ConsoDailyTyping,
    ConsoHourlyTyping,
    ConsoMonthlyTyping,
)
from hydroqc.types.info_compte import (
    ComptesTyping,
    InfoCompteTyping,
    listeComptesContratsTyping,
    listeContratModelTyping,
)
from hydroqc.types.winter_credit import (
    CriticalPeakDataTyping,
    PeriodDataTyping,
    WinterCreditDataTyping,
)

__all__ = [
    "InfoCompteTyping",
    "ConsoHourlyTyping",
    "ConsoDailyTyping",
    "ConsoMonthlyTyping",
    "ConsoAnnualTyping",
    "CriticalPeakDataTyping",
    "PeriodDataTyping",
    "WinterCreditDataTyping",
    "listeComptesContratsTyping",
    "listeContratModelTyping",
    "ComptesTyping",
]
