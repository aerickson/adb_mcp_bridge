import json
import pathlib
import sys
from typing import Any


def _load_config(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Claude config must be a JSON object at the top level.")
    return data


def _ensure_mcp_server(
    config: dict[str, Any],
    *,
    name: str,
    command: str,
    args: list[str],
) -> None:
    mcp_servers = config.setdefault("mcpServers", {})
    if not isinstance(mcp_servers, dict):
        raise ValueError("MCP config 'mcpServers' must be a JSON object.")
    mcp_servers[name] = {
        "type": "stdio",
        "command": command,
        "args": args,
    }


def main(config_path: str) -> int:
    path = pathlib.Path(config_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    config = _load_config(path)
    _ensure_mcp_server(
        config,
        name="adb_mcp_bridge",
        command="adb-mcp-bridge",
        args=[],
    )
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"Updated Claude Desktop MCP config: {path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: install_claude_config.py <config_path>")
    raise SystemExit(main(sys.argv[1]))
