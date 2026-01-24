import json
import pathlib
import sys


def main(config_path: str) -> int:
    path = pathlib.Path(config_path).expanduser()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive for malformed files
        print(f"  ✗ unreadable ({exc})")
        return 1
    servers = data.get("mcpServers", {})
    if isinstance(servers, dict) and "adb_mcp_bridge" in servers:
        print("  ✓ adb_mcp_bridge found")
        return 0
    print("  ✗ adb_mcp_bridge missing")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: check_claude_user_mcp.py <claude_user_config>")
    raise SystemExit(main(sys.argv[1]))
