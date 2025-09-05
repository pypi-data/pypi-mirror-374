import re
import subprocess
from functools import cache

from .utils import clean_name


@cache
def get_processor_name() -> str:
    """Safely get processor name."""
    try:
        cmd = ["lscpu"]
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603
        all_info = proc.stdout.strip()
        for line in all_info.split("\n"):
            if "Model name:" in line:
                return clean_name(re.sub(r"Model name:\s+", "", line, count=1))
        return "--"
    except subprocess.CalledProcessError:  # pragma: no cover
        return "--"


def get_temp_info() -> dict:
    """Get the CPU temperature using vcgencmd."""
    try:
        result = subprocess.run(
            ["/usr/bin/vcgencmd", "measure_temp"],
            capture_output=True,
            text=True,
            check=True,
        )
        temp_c = round(float(result.stdout.split("=")[1].split("'")[0]), 1)
        temp_f = round(temp_c * 9 / 5 + 32, 1)
        return {
            "celsius": temp_c,
            "fahrenheit": temp_f,
            "celsius_str": f"{temp_c} °C",
            "fahrenheit_str": f"{temp_f} °F",
        }
    except subprocess.CalledProcessError:
        return {}
