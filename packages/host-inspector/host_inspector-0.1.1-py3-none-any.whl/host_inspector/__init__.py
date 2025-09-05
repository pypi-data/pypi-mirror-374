from .cpu import get_cpu_info
from .date_time import get_datetime_info
from .disk import get_disk_info
from .firewall import get_firewall_info  # noqa: F401
from .gpu import get_gpu_info
from .memory import get_mem_info
from .network import get_network_info
from .os import get_os_info
from .platform import get_platform_info
from .uptime import get_uptime_info

# from .python import get_python_info

__version__ = "0.1.1"


def get_device_info() -> dict:
    """Return device information."""
    return {
        "os": get_os_info(),
        "platform": get_platform_info(),
        "network": get_network_info(),
        # "python": get_python_info(),  # deprecated 0.3.12
        "gpu": get_gpu_info(),
        # "firewall": get_firewall_info(),
    }


def get_health_info() -> dict:
    """Return overall health information. CPU, Mem, Disk, Uptime."""
    return {
        "cpu": get_cpu_info(),
        "mem": get_mem_info(),
        "disk": get_disk_info(),
        "uptime": get_uptime_info(),
        "local_datetime": get_datetime_info(),
    }
