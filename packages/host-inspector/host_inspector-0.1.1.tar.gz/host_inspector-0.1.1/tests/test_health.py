from host_inspector import get_health_info


def test_get_health_info():
    health_info = get_health_info()

    assert isinstance(health_info, dict)
    assert set(health_info.keys()) == {
        "cpu",
        "mem",
        "disk",
        "uptime",
        "local_datetime",
    }

    for value in health_info.values():
        assert isinstance(value, dict)
