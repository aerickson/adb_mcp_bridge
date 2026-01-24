PYTHON ?= python3
CODEX_CONFIG ?= $(HOME)/.codex/config.toml
CLAUDE_CONFIG ?= $(CURDIR)/.mcp.json

.PHONY: install install-codex install-claude install-claude-global uninstall-claude-global install-pipx doctor

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

install-claude-global:
	@claude mcp add-json --scope user adb_mcp_bridge '{"type":"stdio","command":"adb-mcp-bridge","args":[]}'

uninstall-claude-global:
	@claude mcp remove --scope user adb_mcp_bridge

doctor:
	@echo "Claude config: $(CLAUDE_CONFIG)"
	@echo "Codex config:  $(CODEX_CONFIG)"
	@echo "adb-mcp-bridge in PATH:"
	@command -v adb-mcp-bridge || true
	@echo "adb devices -l:"
	@adb devices -l || true
