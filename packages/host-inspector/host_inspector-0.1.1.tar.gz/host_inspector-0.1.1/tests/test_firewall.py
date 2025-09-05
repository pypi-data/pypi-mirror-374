import os

import pytest

from host_inspector import get_firewall_info


@pytest.mark.skipif(os.name != "nt", reason="Windows only")
@pytest.mark.parametrize(
    ("ports", "direction", "enabled_only", "exclude_any_ports"),
    [
        ([80], "in", True, False),
        ([22, 443], "out", False, True),
        ([], "in", False, False),
    ],
)
def test_get_firewall_info_variants(ports, direction, enabled_only, exclude_any_ports):
    firewall_info = get_firewall_info(
        interested_ports=ports,
        direction=direction,
        enabled_only=enabled_only,
        exclude_any_ports=exclude_any_ports,
    )
    assert isinstance(firewall_info, dict)
    assert "status" in firewall_info
    assert "rules" in firewall_info
    assert isinstance(firewall_info["rules"], list)


@pytest.mark.skipif(os.name != "nt", reason="Windows only")
def test_get_firewall_info_empty_ports():
    firewall_info = get_firewall_info(interested_ports=[])
    assert isinstance(firewall_info, dict)
    assert "status" in firewall_info
    assert "rules" in firewall_info


@pytest.mark.skipif(os.name != "nt", reason="Windows only")
def test_check_firewall_status_true_false():
    from host_inspector.firewall.windows import check_firewall_status  # noqa: PLC0415

    result = check_firewall_status()
    assert isinstance(result, bool)


@pytest.mark.skipif(os.name != "nt", reason="Windows only")
def test_is_firewall_enabled_profiles_keys():
    from host_inspector.firewall.windows import is_firewall_enabled  # noqa: PLC0415

    status = is_firewall_enabled()
    assert isinstance(status, dict)

    assert set(status.keys()) == {"domain", "private", "public", "overall"}
    # print(status)


@pytest.mark.skipif(os.name != "nt", reason="Windows only")
def test_is_firewall_enabled_return_type():
    from host_inspector.firewall.windows import is_firewall_enabled  # noqa: PLC0415

    status = is_firewall_enabled()
    assert isinstance(status, dict)
    assert any(isinstance(v, bool) for v in status.values())
