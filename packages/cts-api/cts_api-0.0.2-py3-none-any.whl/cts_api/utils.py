"""Utils for API."""

from datetime import timedelta


def timedelta_isoformat(td: timedelta) -> str:
    """ISO 8601 encoding for Python timedelta object."""
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{"-" if td.days < 0 else ""}P{abs(td.days)}DT{hours:d}H{minutes:d}M{seconds:d}.{td.microseconds:06d}S'
