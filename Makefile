PYTHON ?= python3
CODEX_CONFIG ?= $(HOME)/.codex/config.toml
CLAUDE_CONFIG ?= $(HOME)/Library/Application Support/Claude/claude_desktop_config.json

.PHONY: install install-codex install-claude install-pipx

install: install-pipx install-codex install-claude

install-pipx:
	@pipx install -e .

install-codex:
	@mkdir -p "$(dir $(CODEX_CONFIG))"
	@touch "$(CODEX_CONFIG)"
	@if grep -q '^\[mcp_servers\.adb_mcp_bridge\]' "$(CODEX_CONFIG)"; then \
		echo "Codex config already contains adb_mcp_bridge entry."; \
	else \
		printf '\n[mcp_servers.adb_mcp_bridge]\ncommand = "adb-mcp-bridge"\nargs = []\nstartup_timeout_sec = 20\ntool_timeout_sec = 60\n' >> "$(CODEX_CONFIG)"; \
		echo "Added adb_mcp_bridge MCP server to $(CODEX_CONFIG)"; \
	fi

install-claude:
	@$(PYTHON) scripts/install_claude_config.py "$(CLAUDE_CONFIG)"
