PYTHON ?= python3
CODEX_CONFIG ?= $(HOME)/.codex/config.toml
CLAUDE_CONFIG ?= $(CURDIR)/.mcp.json
CLAUDE_USER_CONFIG ?= $(HOME)/.claude.json

.PHONY: install install-codex install-claude install-claude-global uninstall-claude-global install-pipx doctor

install: install-pipx install-codex install-claude-global

install-pipx:
	@pipx install -e . --force

install-codex:
	@if [ -f "$(CODEX_CONFIG)" ]; then \
		:; \
	else \
		mkdir -p "$(dir $(CODEX_CONFIG))"; \
		touch "$(CODEX_CONFIG)"; \
	fi; \
	if grep -q '^\[mcp_servers\.adb_mcp_bridge\]' "$(CODEX_CONFIG)" 2>/dev/null; then \
		echo "Codex config already contains adb_mcp_bridge entry."; \
	else \
		printf '\n[mcp_servers.adb_mcp_bridge]\ncommand = "adb-mcp-bridge"\nargs = []\nstartup_timeout_sec = 20\ntool_timeout_sec = 60\n' >> "$(CODEX_CONFIG)"; \
		echo "Added adb_mcp_bridge MCP server to $(CODEX_CONFIG)"; \
	fi

install-claude:
	@$(PYTHON) scripts/install_claude_config.py "$(CLAUDE_CONFIG)"
	@echo "To install for another repo, run:"
	@echo "  claude mcp add-json --scope project adb_mcp_bridge '{\"type\":\"stdio\",\"command\":\"adb-mcp-bridge\",\"args\":[]}'"

install-claude-global:
	@if [ -f "$(CLAUDE_USER_CONFIG)" ] && $(PYTHON) scripts/check_claude_user_mcp.py "$(CLAUDE_USER_CONFIG)" >/dev/null 2>&1; then \
		echo "Claude CLI: adb_mcp_bridge already exists in user config."; \
	else \
		claude mcp add-json --scope user adb_mcp_bridge '{"type":"stdio","command":"adb-mcp-bridge","args":[]}'; \
		if [ -f "$(CLAUDE_USER_CONFIG)" ] && $(PYTHON) scripts/check_claude_user_mcp.py "$(CLAUDE_USER_CONFIG)" >/dev/null 2>&1; then \
			echo "Claude CLI: adb_mcp_bridge installed in user config."; \
		else \
			exit 1; \
		fi; \
	fi

uninstall-claude-global:
	@claude mcp remove --scope user adb_mcp_bridge

doctor:
	@echo "Claude user config: $(CLAUDE_USER_CONFIG)"
	@total=0; success=0; \
	if [ -f "$(CLAUDE_USER_CONFIG)" ]; then \
		total=$$((total+1)); \
		if $(PYTHON) scripts/check_claude_user_mcp.py "$(CLAUDE_USER_CONFIG)"; then success=$$((success+1)); fi; \
	else \
		total=$$((total+1)); \
		echo "  ✗ missing"; \
	fi; \
	echo "Codex config:  $(CODEX_CONFIG)"; \
	total=$$((total+1)); \
	if [ -f "$(CODEX_CONFIG)" ]; then echo "  ✓ found"; success=$$((success+1)); else echo "  ✗ missing"; fi; \
	echo "adb-mcp-bridge in PATH:"; \
	total=$$((total+1)); \
	if command -v adb-mcp-bridge >/dev/null 2>&1; then echo "  ✓ found"; success=$$((success+1)); else echo "  ✗ missing"; fi; \
	echo "adb devices -l:"; \
	total=$$((total+1)); \
	if adb devices -l >/dev/null 2>&1; then echo "  ✓ ok"; success=$$((success+1)); else echo "  ✗ failed"; fi; \
	adb devices -l || true; \
	echo "Summary: $$success/$$total checks passed"
