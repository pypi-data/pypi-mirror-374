# src/tdt/core.py
from datetime import datetime
from dateutil.relativedelta import relativedelta

def count_ticks(start: datetime = None, end: datetime = None, unit: str = "seconds") -> int:
    """
    Count ticks between two datetimes in the chosen unit.
    
    Args:
        start (datetime): starting time (default = Unix epoch 1970-01-01).
        end (datetime): ending time (default = now).
        unit (str): tick unit, one of:
            "years", "months", "days", "hours",
            "minutes", "seconds", "milliseconds",
            "microseconds", "nanoseconds"
    
    Returns:
        int: number of ticks between start and end.
    """
    if start is None:
        start = datetime(1970, 1, 1)
    if end is None:
        end = datetime.now()

    if unit in {"years", "months"}:
        # Use relativedelta for calendar math
        delta = relativedelta(end, start)
        if unit == "years":
            return delta.years + delta.months / 12 + delta.days / 365
        elif unit == "months":
            return delta.years * 12 + delta.months + delta.days / 30
    else:
        # Convert to timestamps for precise ticks
        delta_seconds = (end - start).total_seconds()
        if unit == "days":
            return int(delta_seconds // 86400)
        elif unit == "hours":
            return int(delta_seconds // 3600)
        elif unit == "minutes":
            return int(delta_seconds // 60)
        elif unit == "seconds":
            return int(delta_seconds)
        elif unit == "milliseconds":
            return int(delta_seconds * 1_000)
        elif unit == "microseconds":
            return int(delta_seconds * 1_000_000)
        elif unit == "nanoseconds":
            return int(delta_seconds * 1_000_000_000)
        else:
            raise ValueError(f"Unsupported unit: {unit}")

def breakdown(start: datetime, end: datetime) -> dict:
    """
    Break down elapsed time into multiple units.
    Returns dict with years, months, days, hours, minutes, seconds.
    """
    delta = relativedelta(end, start)
    return {
        "years": delta.years,
        "months": delta.months,
        "days": delta.days,
        "hours": delta.hours,
        "minutes": delta.minutes,
        "seconds": delta.seconds,
    }
def breakdown_all(start: datetime, end: datetime = None) -> dict:
    """
    Return elapsed time between start and end in multiple units
    (from millennia down to nanoseconds).

    Args:
        start (datetime): starting datetime
        end (datetime, optional): ending datetime (default = now)

    Returns:
        dict: elapsed time in different units
    """
    if end is None:
        end = datetime.now()

    # Use relativedelta for years/months/days
    delta = relativedelta(end, start)
    total_days = (end - start).days
    total_seconds = (end - start).total_seconds()

    return {
        "millennia": total_days // (365_000),  # 1000 years
        "centuries": total_days // (36_500),   # 100 years
        "decades": total_days // (3_650),      # 10 years
        "years": delta.years + delta.months / 12 + delta.days / 365,
        "months": delta.years * 12 + delta.months + delta.days / 30,
        "weeks": total_days // 7,
        "days": total_days,
        "hours": int(total_seconds // 3600),
        "minutes": int(total_seconds // 60),
        "seconds": int(total_seconds),
        "milliseconds": int(total_seconds * 1_000),
        "microseconds": int(total_seconds * 1_000_000),
        "nanoseconds": int(total_seconds * 1_000_000_000),
    }

def pretty_breakdown(start: datetime, end: datetime = None, max_units: int = 3) -> str:
    """
    Return a human-readable string for elapsed time between two datetimes.

    Args:
        start (datetime): starting datetime
        end (datetime, optional): ending datetime (default = now)
        max_units (int): maximum number of units to include (default = 3)

    Returns:
        str: e.g. "27 years, 5 months, 12 days"
    """
    if end is None:
        end = datetime.now()

    delta = relativedelta(end, start)

    parts = []
    if delta.years:
        parts.append(f"{delta.years} year{'s' if delta.years != 1 else ''}")
    if delta.months:
        parts.append(f"{delta.months} month{'s' if delta.months != 1 else ''}")
    if delta.days:
        parts.append(f"{delta.days} day{'s' if delta.days != 1 else ''}")
    if delta.hours:
        parts.append(f"{delta.hours} hour{'s' if delta.hours != 1 else ''}")
    if delta.minutes:
        parts.append(f"{delta.minutes} minute{'s' if delta.minutes != 1 else ''}")
    if delta.seconds and not parts:  # only show seconds if nothing else
        parts.append(f"{delta.seconds} second{'s' if delta.seconds != 1 else ''}")

    # Limit to max_units
    parts = parts[:max_units]

    return ", ".join(parts) if parts else "0 seconds"


if __name__ == "__main__":
    from datetime import datetime

    start = datetime(1997, 6, 15)
    end = datetime.now()

    print(pretty_breakdown(start, end))          # → "27 years, 5 months, 18 days"
    print(pretty_breakdown(start, end, 2))       # → "27 years, 5 months"
    print(pretty_breakdown(end, end))            # → "0 seconds"
