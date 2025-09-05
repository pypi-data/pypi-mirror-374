from host_inspector import get_gpu_info


def test_get_gpu_info():
    gpu_info = get_gpu_info()

    assert isinstance(gpu_info, dict)

    assert set(gpu_info.keys()) == {"model", "vram", "resolution", "refresh_rate"}

    # If you want to check that the values are not None
    # for key, value in gpu_info.items():
    #     assert value is not None, f'Key "{key}" is None.'
