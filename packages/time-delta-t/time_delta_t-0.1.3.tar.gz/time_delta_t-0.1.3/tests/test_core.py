import pytest
from datetime import datetime, timedelta
from tdt.core import count_ticks, breakdown, breakdown_all, pretty_breakdown

def test_count_ticks_default_now():
    # Defaults: epoch → now, in seconds
    ticks = count_ticks()
    assert isinstance(ticks, int)
    assert ticks > 0

def test_count_ticks_units():
    start = datetime(2000, 1, 1)
    end = datetime(2000, 1, 2)

    assert count_ticks(start, end, "days") == 1
    assert count_ticks(start, end, "hours") == 24
    assert count_ticks(start, end, "minutes") == 1440
    assert count_ticks(start, end, "seconds") == 86400
    assert count_ticks(start, end, "milliseconds") == 86_400_000
    assert count_ticks(start, end, "microseconds") == 86_400_000_000
    assert count_ticks(start, end, "nanoseconds") == 86_400_000_000_000

def test_breakdown():
    start = datetime(2000, 1, 1)
    end = datetime(2001, 2, 3, 4, 5, 6)

    b = breakdown(start, end)
    assert b["years"] == 1
    assert b["months"] == 1
    assert b["days"] >= 0
    assert b["hours"] == 4
    assert b["minutes"] == 5
    assert isinstance(b["seconds"], int)

def test_breakdown_all_consistency():
    start = datetime(2000, 1, 1)
    end = start + timedelta(days=10)

    b = breakdown_all(start, end)
    assert b["days"] == 10
    assert b["weeks"] == 1  # 10 days → 1 week (integer floor)
    assert b["hours"] == 240
    assert b["minutes"] == 14_400
    assert b["seconds"] == 864_000

def test_pretty_breakdown():
    start = datetime(2000, 1, 1)
    end = datetime(2002, 2, 15)

    pretty = pretty_breakdown(start, end)

    # Helper to allow singular or plural
    def contains_unit(s, unit):
        return (unit in s) or (unit.rstrip('s') in s)

    assert contains_unit(pretty, "years")
    assert contains_unit(pretty, "months")
    assert contains_unit(pretty, "days")

    # limit units
    short = pretty_breakdown(start, end, max_units=1)
    assert "," not in short
