import base64
import pathlib
import subprocess
import time
from typing import Optional, TypedDict

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("adb-mcp-bridge")


class ScreenshotResult(TypedDict):
    path: str
    bytes: int
    timestamp: int
    mime_type: str
    base64_png: Optional[str]


def _ensure_device_ready(serial: str) -> None:
    proc = subprocess.run(
        ["adb", "-s", serial, "get-state"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=8,
    )
    state = (proc.stdout or b"").decode(errors="ignore").strip()
    if proc.returncode != 0 or state != "device":
        err = (proc.stderr or b"").decode(errors="ignore").strip()
        raise RuntimeError(f"adb device not ready (state={state}). {err}")


def _parse_adb_devices(output: str) -> list[tuple[str, str]]:
    devices: list[tuple[str, str]] = []
    for line in output.splitlines():
        line = line.strip()
        if (
            not line
            or line.startswith("List of devices attached")
            or line.startswith("* daemon not running")
            or line.startswith("* daemon started successfully")
        ):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        serial, state = parts[0], parts[1]
        devices.append((serial, state))
    return devices


def _select_single_emulator(devices: list[tuple[str, str]]) -> str:
    if not devices:
        raise RuntimeError("adb: no devices detected")
    if len(devices) > 1:
        serials = ", ".join(serial for serial, _ in devices)
        raise RuntimeError(f"adb: multiple devices detected ({serials})")

    serial, state = devices[0]
    if state == "offline":
        raise RuntimeError(f"adb: device offline (serial={serial})")
    if state == "unauthorized":
        raise RuntimeError(f"adb: device unauthorized (serial={serial})")
    if state != "device":
        raise RuntimeError(f"adb: device in unexpected state (state={state}, serial={serial})")
    if not serial.startswith("emulator-"):
        raise RuntimeError(f"adb: non-emulator device detected (serial={serial})")

    return serial


def _discover_single_emulator() -> str:
    proc = subprocess.run(
        ["adb", "devices", "-l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=8,
    )
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode(errors="ignore").strip()
        raise RuntimeError(f"adb devices failed. {err}")

    output = (proc.stdout or b"").decode(errors="ignore")
    devices = _parse_adb_devices(output)
    return _select_single_emulator(devices)


@mcp.tool()
def take_screenshot(
    *,
    output_dir: str = "./screenshots",
    include_base64: bool = False,
) -> ScreenshotResult:
    """
    Capture a PNG screenshot from an Android emulator via ADB.
    """
    active_serial = _discover_single_emulator()
    _ensure_device_ready(active_serial)

    out_dir = pathlib.Path(output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = int(time.time())
    path = out_dir / f"screenshot_{active_serial}_{ts}.png"

    cmd = ["adb", "-s", active_serial, "exec-out", "screencap", "-p"]
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )

    if proc.returncode != 0:
        err = (proc.stderr or b"").decode(errors="ignore")
        raise RuntimeError(f"adb screencap failed: {err}")

    path.write_bytes(proc.stdout)

    b64 = None
    if include_base64:
        b64 = base64.b64encode(proc.stdout).decode("ascii")

    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "timestamp": ts,
        "mime_type": "image/png",
        "base64_png": b64,
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
