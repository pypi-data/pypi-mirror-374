import time
from datetime import datetime
from functools import cache

import psutil

from .utils.datetimeutils import human_delta


@cache
def boot_time() -> datetime:
    """Return datetime of CPU boot time."""
    return datetime.fromtimestamp(psutil.boot_time()).astimezone()


@cache
def boot_date_as_string() -> str:
    """Return boot time date as string."""
    return boot_time().strftime("%Y-%m-%d")


@cache
def boot_time_as_string() -> str:
    """Return boot time as string."""
    return boot_time().strftime("%I:%M:%S %p")


@cache
def boot_date_as_day() -> str:
    """Return boot time as day string."""
    return boot_time().strftime("%A, %B %d")


def uptime_in_seconds() -> int:
    """Return uptime in seconds."""
    return int(time.time() - psutil.boot_time())


def uptime_as_string() -> str:
    """Return uptime as string."""
    return human_delta(uptime_in_seconds())


def get_uptime_info() -> dict:
    """Return uptime info as a dict."""
    return {
        "day": boot_date_as_day(),
        "date": boot_date_as_string(),
        "time": boot_time_as_string(),
        "uptime": uptime_as_string(),
        "seconds": uptime_in_seconds(),
    }
