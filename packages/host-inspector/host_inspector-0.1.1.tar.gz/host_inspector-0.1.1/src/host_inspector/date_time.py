import time
from datetime import datetime


def is_dst() -> bool:
    """Return True if Daylight Savings Time."""
    return time.localtime().tm_isdst == 1


def local_timezone() -> str:
    """Get local Timezone."""
    return str(datetime.now().astimezone().tzinfo)


def date_as_string() -> str:
    """Return boot time date as string."""
    now = datetime.now().astimezone()
    return now.strftime("%Y-%m-%d")


def date_as_day(abbreviated=False) -> str:
    """Return date as a string."""
    now = datetime.now().astimezone()
    return now.strftime("%a %b %d") if abbreviated else now.strftime("%A, %B %d")


def time_as_string(military=False) -> str:
    """Return time as a string."""
    now = datetime.now().astimezone()
    return now.strftime("%H:%M") if military else now.strftime("%I:%M %p")


def get_datetime_info() -> dict:
    """Get date/time information as a dict."""
    return {
        "day": date_as_day(),
        "date": date_as_string(),
        "time": time_as_string(),
        "military_time": time_as_string(military=True),
        "timezone": local_timezone(),
        "is_dst": is_dst(),
    }
