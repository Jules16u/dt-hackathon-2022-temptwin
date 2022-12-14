"""TimeRange tests for hydroqc."""
import datetime

import pytest
from hydroqc.error import HydroQcWinterCreditError
from hydroqc.winter_credit.consts import EST_TIMEZONE
from hydroqc.winter_credit.peak import Anchor, Peak, PreHeat
from hydroqc.winter_credit.timerange import TimeRange

from hydroqc.types import CriticalPeakDataTyping


def test_timerange() -> None:
    """Test timerange features."""
    end_date = datetime.datetime.now().astimezone(EST_TIMEZONE)
    start_date = end_date - datetime.timedelta(days=7)
    time_range = TimeRange(start_date, end_date, False)
    assert time_range.is_critical is False
    assert time_range.start_date == start_date
    assert time_range.end_date == end_date
    assert repr(time_range).startswith("<TimeRange - ")


def test_anchor() -> None:
    """Test all anchor features."""
    end_date = datetime.datetime.now().astimezone(EST_TIMEZONE)
    start_date = end_date - datetime.timedelta(days=7)
    anchor = Anchor(start_date, end_date, True)
    assert anchor.is_critical is True
    assert anchor.start_date == start_date
    assert anchor.end_date == end_date
    assert repr(anchor).startswith("<Anchor - ")


def test_preheat() -> None:
    """Test all preheat features."""
    end_date = datetime.datetime.now().astimezone(EST_TIMEZONE)
    start_date = end_date - datetime.timedelta(days=7)
    pre_heat = PreHeat(start_date, end_date, False)
    assert pre_heat.is_critical is False
    assert pre_heat.start_date == start_date
    assert pre_heat.end_date == end_date
    assert repr(pre_heat).startswith("<PreHeat - ")


def test_peak() -> None:
    """Test all peak features."""
    tmp_date = datetime.datetime.now().astimezone(EST_TIMEZONE)
    start_date = tmp_date - datetime.timedelta(days=7)
    with pytest.raises(HydroQcWinterCreditError):
        evening_peak = Peak(start_date, "bad_value")

    evening_peak = Peak(start_date, "evening")
    stats: CriticalPeakDataTyping = {
        "montantEffacee": 4,
        "consoReference": 1000,
        "consoReelle": 800,
        "consoEffacee": 200,
        "codeConso": "D",
        "indFacture": False,
    }
    evening_peak.set_critical(stats)
    assert evening_peak.is_critical is True
    assert evening_peak.is_morning is False
    assert evening_peak.is_evening is True
    assert evening_peak.day == start_date.date()
    assert evening_peak.anchor.is_critical is True
    assert evening_peak.preheat.is_critical is True

    assert evening_peak.start_date.date() == start_date.date()
    assert evening_peak.end_date.date() == start_date.date()
    assert evening_peak.credit == stats["montantEffacee"]
    assert evening_peak.ref_consumption == stats["consoReference"]
    assert evening_peak.actual_consumption == stats["consoReelle"]
    assert evening_peak.saved_consumption == stats["consoEffacee"]
    assert evening_peak.consumption_code == stats["codeConso"]
    assert evening_peak.is_billed == stats["indFacture"]

    morning_peak = Peak(start_date, "morning")
    assert morning_peak.start_date.date() == start_date.date()
    assert morning_peak.end_date.date() == start_date.date()
    assert morning_peak.is_morning is True
    assert morning_peak.is_evening is False
