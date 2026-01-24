# adb-mcp-bridge

**adb-mcp-bridge** is a local **MCP (Model Context Protocol) stdio server** that exposes safe,
structured access to Android emulators via **ADB** for use by AI agents such as **Codex** and
**Claude**.

The project focuses on safety, determinism, and clean extensibility. Agents never get raw shell
access, and all device state is managed by the bridge, not the model.

---

## Features

### v1.0
- Take screenshots from a running Android emulator
- Single-device support
- Emulator-only enforcement (`emulator-*`)
- Structured MCP tool interface
- Safe by default (no arbitrary `adb shell`)

Planned (v1.0+):
- Multiple device support
- UI interaction (tap, swipe, input)
- UI inspection (uiautomator dumps)
- App lifecycle management
- Per-device state and locking

---

## Requirements

- Python 3.9+
- Android SDK with `adb` on your PATH
- At least one running Android emulator
- An MCP-capable agent (Codex, Claude Desktop, etc.)

---

## Installation

```bash
git clone <repo-url>
cd adb-mcp-bridge
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
uv pip install -e .
```

---

## Install MCP configs (Makefile)

```bash
pipx install -e .
make install-codex
make install-claude
```

Claude Desktop config defaults to `~/Library/Application Support/Claude/claude_desktop_config.json`.
Override with `CLAUDE_CONFIG=/path/to/config.json`.

---

## Debugging setup

```bash
make doctor
```

This prints the config paths, resolves `adb-mcp-bridge` from your PATH, and shows `adb devices -l`.

---

## Running tests

```bash
uv sync --extra dev
uv run pytest
```

---

## Running the MCP server

```bash
adb-mcp-bridge
```

The process runs as a **stdio MCP server** and waits for requests from an agent.

---

## MCP Tool: take_screenshot

Capture a PNG screenshot from the active Android emulator.

**Inputs**
- `output_dir` (optional, default `./screenshots`)
- `include_base64` (optional, default `false`)

**Outputs**
- `path` – filesystem path to the PNG
- `bytes` – file size
- `timestamp` – unix timestamp
- `mime_type` – `image/png`
- `base64_png` – optional base64 image data

The tool fails if:
- no device is available,
- more than one device is connected,
- the device is not an emulator,
- the device is offline or unauthorized.

---

## Using with Codex

Add the server to your Codex MCP configuration (`~/.codex/config.toml`):

```toml
[mcp_servers.adb_mcp_bridge]
command = "adb-mcp-bridge"
args = []
startup_timeout_sec = 20
tool_timeout_sec = 60
```

Restart Codex and the `take_screenshot` tool will be available.

---

## Using with Claude Desktop

`adb-mcp-bridge` can be used:
- directly as a stdio MCP server, or
- wrapped in a Claude Desktop `.mcpb` extension.

Refer to Claude Desktop MCP documentation for your platform-specific configuration.

---

## Using the MCP tools

Once the MCP server is configured (Codex or Claude Desktop), you can call the
`take_screenshot` tool. It accepts only keyword arguments:

```json
{
  "output_dir": "./screenshots",
  "include_base64": false
}
```

Notes:
- The active device is auto-selected; exactly one emulator must be connected.
- Errors are returned if no devices are found, multiple devices are connected, or the device is offline/unauthorized.

---

## Safety model

- Explicit tool interfaces only
- No raw shell execution
- Emulator-only by default
- Timeouts on all ADB operations
- Deterministic, structured errors

---

## Project status

- **Status:** Early development
- **Current version:** v1.0 (screenshots only)
- **API stability:** Experimental

---

## License

Mozilla Public License v2.0 (see `LICENSE`).
