import shlex
import subprocess
from functools import cache

from host_inspector.utils.byteutils import bytes_to_gib

from .utils import clean_name


@cache
def get_gpu():
    """Safely get GPU."""
    try:
        cmd = "powershell Get-WmiObject win32_VideoController"
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd),
            check=True,
            capture_output=True,
            text=True,
        )
        return proc.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def _get_key_value(line):
    """Split text output and return a key, value pair."""
    parts = line.split(":")
    key = parts.pop(0).strip()
    value = ":".join(parts).strip()
    return (key, value)


def _get_key(find_key):
    """Get Key from GPU output."""
    if result := get_gpu():
        lines = result.split("\n")
        # lines.reverse()
        for line in lines:
            key, value = _get_key_value(line)
            if key == find_key:
                return value
    return None


@cache
def get_model() -> str:
    """Get GPU chipset model."""
    if name := _get_key("Description"):
        return clean_name(name)
    return "--"


@cache
def get_vram() -> str:
    """Get GPU VRAM."""
    if _bytes := _get_key("AdapterRAM"):
        return f"{bytes_to_gib(int(_bytes))} GB"
    return "--"


@cache
def get_resolution() -> str:
    """Get resolution."""
    hres = _get_key("CurrentHorizontalResolution")
    vres = _get_key("CurrentVerticalResolution")
    return f"{hres} x {vres}"


@cache
def get_refresh_rate() -> str:
    # TODO: Get Refresh Rate.
    return "--"


@cache
def get_gpu_info() -> dict:
    """Return a dict of GPU info."""
    return {
        "model": get_model(),
        "vram": get_vram(),
        "resolution": get_resolution(),
        "refresh_rate": get_refresh_rate(),
    }
