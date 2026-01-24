# Product Spec: adb-mcp-bridge

## Overview

**adb-mcp-bridge** is a local MCP (Model Context Protocol) server that exposes safe, structured Android device control via ADB for use by AI agents (Codex, Claude, etc).

The goal is to allow agents to interact with Android emulators in a deterministic, constrained way, without granting arbitrary shell access, and without relying on the agent to track fragile device state.

---

## Goals

### v1.0
- Provide a single, reliable capability: take a screenshot of the current Android device.
- Support exactly one active device.
- Be safe by default and easy to integrate with MCP-capable agents.
- Establish a clean foundation for future expansion.

### v1.0+
- Expand to additional ADB-backed actions.
- Support multiple concurrent devices.
- Introduce explicit device selection and per-device state.
- Enable higher-level workflows (UI interaction, inspection, automation).

---

## Non-Goals (v1.0)

- No physical device support.
- No UI interaction (tap, swipe, text input).
- No test orchestration or scenario execution.
- No cloud or remote execution.
- No arbitrary `adb shell` passthrough.

---

## Architecture

### High-level design

```
AI Agent (Codex / Claude)
        |
        | MCP (stdio)
        |
adb-mcp-bridge (local process)
        |
        | adb
        |
Android Emulator
```

- `adb-mcp-bridge` runs locally and communicates with the agent over MCP stdio.
- All interaction with Android occurs via `adb`.
- The bridge enforces safety and invariants before executing any ADB command.

---

## v1.0 Scope

### Device model

- Exactly one active device.
- The device is assumed to be:
  - already running,
  - an emulator,
  - reachable via `adb`.
- The device is identified implicitly:
  - either the only connected device, or
  - a fixed configured serial (implementation detail).

The agent does not manage device identity in v1.0.

---

### Supported tools (v1.0)

#### `take_screenshot`

**Description**  
Capture a PNG screenshot from the active Android emulator.

**Implementation**
- Uses `adb exec-out screencap -p`
- Writes the screenshot to disk
- Optionally returns base64-encoded image data

**Inputs**
- `output_dir` (optional, default `./screenshots`)
- `include_base64` (optional, default `false`)

**Outputs**
- `path`: filesystem path to the PNG
- `bytes`: file size
- `timestamp`: unix timestamp
- `mime_type`: `image/png`
- `base64_png` (optional)

**Constraints**
- Fails if:
  - no device is available,
  - more than one device is detected,
  - the device is not an emulator,
  - the device is offline or unauthorized.

---

## Safety guarantees (v1.0)

- No arbitrary command execution.
- No `adb shell` passthrough.
- Explicit allowlist of ADB operations.
- Emulator-only enforcement.
- Timeouts on all ADB calls.
- Structured errors returned to the agent.

### Future config: physical device allowlist

Physical devices remain blocked by default. A future config file (TOML) can allow
specific physical device serials while always permitting emulators.

Example:

```toml
[device]
allowlist = ["0123456789ABCDEF"]
```

Behavior:
- Emulators are always allowed.
- Non-emulator devices are allowed only if their serial is listed in `allowlist`.
  If the list is missing or empty, no physical devices are allowed.

---

## v1.0+ Roadmap

### Device handling

- Explicit device enumeration:
  - `list_devices`
  - `select_device(serial)`
- Support multiple concurrent devices.
- Per-device locking to prevent concurrent command conflicts.
- Optional session abstraction per device.

---

### Expanded toolset

Potential additions:
- UI interaction:
  - `tap`
  - `swipe`
  - `input_text`
  - `keyevent`
- UI inspection:
  - `uiautomator_dump`
  - focused activity/window info
- App lifecycle:
  - `install_apk`
  - `start_activity`
  - `force_stop`
- Observability:
  - `logcat` (filtered, bounded)

All new tools must follow the same safety and structure constraints as v1.0.

---

### State management

- State is owned by the bridge, not the agent.
- Examples of bridge-managed state:
  - active device selection,
  - last screenshot metadata,
  - device readiness status,
  - per-device locks.
- The agent treats the bridge as the source of truth.

---

## Compatibility

- MCP protocol compliant.
- Works with:
  - Codex (stdio MCP servers),
  - Claude Desktop (via stdio or `.mcpb` wrapper).
- Packaging and naming designed to support both without code duplication.

---

## Success criteria

### v1.0 is successful if:
- An agent can reliably request screenshots without ambiguity.
- Failures are deterministic and actionable.
- The system remains safe even with malformed or adversarial prompts.
- Adding a second tool does not require architectural changes.

---

## Why MCP (not a skill)

This project is an MCP server (not a prompt/skill wrapper) to provide a structured,
typed tool interface with deterministic inputs/outputs, timeouts, and clear error
handling. MCP also isolates ADB access behind explicit tools, reducing the risk of
arbitrary shell execution while keeping the surface area small and auditable.
