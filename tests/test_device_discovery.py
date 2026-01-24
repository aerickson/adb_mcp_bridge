import pytest

from adb_mcp_bridge import server


def test_parse_adb_devices_empty() -> None:
    output = "List of devices attached\n\n"
    assert server._parse_adb_devices(output) == []


def test_parse_adb_devices_multiple_lines() -> None:
    output = (
        "List of devices attached\n"
        "emulator-5554 device product:sdk_gphone64_x86_64 model:sdk_gphone64_x86_64\n"
        "emulator-5556 unauthorized usb:1-1\n"
    )
    assert server._parse_adb_devices(output) == [
        ("emulator-5554", "device"),
        ("emulator-5556", "unauthorized"),
    ]


def test_parse_adb_devices_ignores_daemon_lines() -> None:
    output = (
        "* daemon not running; starting now at tcp:5037\n"
        "* daemon started successfully\n"
        "List of devices attached\n"
        "emulator-5554 device product:sdk_gphone64_x86_64 model:sdk_gphone64_x86_64\n"
    )
    assert server._parse_adb_devices(output) == [("emulator-5554", "device")]


def test_select_single_emulator_none() -> None:
    with pytest.raises(RuntimeError, match="no devices detected"):
        server._select_single_emulator([])


def test_select_single_emulator_multiple() -> None:
    devices = [("emulator-5554", "device"), ("emulator-5556", "device")]
    with pytest.raises(RuntimeError, match="multiple devices detected"):
        server._select_single_emulator(devices)


def test_select_single_emulator_offline() -> None:
    with pytest.raises(RuntimeError, match="device offline"):
        server._select_single_emulator([("emulator-5554", "offline")])


def test_select_single_emulator_unauthorized() -> None:
    with pytest.raises(RuntimeError, match="device unauthorized"):
        server._select_single_emulator([("emulator-5554", "unauthorized")])


def test_parse_adb_devices_no_permissions_state() -> None:
    output = "0123456789ABCDEF no permissions (user in plugdev group)\n"
    assert server._parse_adb_devices(output) == [("0123456789ABCDEF", "no_permissions")]


def test_select_single_emulator_no_permissions() -> None:
    with pytest.raises(RuntimeError, match="no permissions"):
        server._select_single_emulator([("0123456789ABCDEF", "no_permissions")])


def test_select_single_emulator_unexpected_state() -> None:
    with pytest.raises(RuntimeError, match="unexpected state"):
        server._select_single_emulator([("emulator-5554", "bootloader")])


def test_select_single_emulator_non_emulator() -> None:
    with pytest.raises(RuntimeError, match="non-emulator device"):
        server._select_single_emulator([("0123456789ABCDEF", "device")])


def test_select_single_emulator_success() -> None:
    assert server._select_single_emulator([("emulator-5554", "device")]) == "emulator-5554"
