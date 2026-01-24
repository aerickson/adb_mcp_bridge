import base64
import pathlib
import subprocess
import time
from typing import Optional, TypedDict

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("adb-mcp-bridge")


class ScreenshotResult(TypedDict):
    serial: str
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


@mcp.tool()
def take_screenshot(
    serial: str,
    output_dir: str = "./screenshots",
    include_base64: bool = False,
) -> ScreenshotResult:
    \"\"\"
    Capture a PNG screenshot from an Android emulator via ADB.
    \"\"\"
    if not serial.startswith("emulator-"):
        raise ValueError("Only emulator-* serials are allowed by default")

    _ensure_device_ready(serial)

    out_dir = pathlib.Path(output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = int(time.time())
    path = out_dir / f"screenshot_{serial}_{ts}.png"

    cmd = ["adb", "-s", serial, "exec-out", "screencap", "-p"]
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
        "serial": serial,
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
