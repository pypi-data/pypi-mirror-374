from host_inspector import get_device_info


def test_get_device_info():
    device_info = get_device_info()

    assert isinstance(device_info, dict)
    assert set(device_info.keys()) == {"os", "platform", "network", "gpu"}

    for value in device_info.values():
        assert isinstance(value, dict)
