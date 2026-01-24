# Agent Instructions

## README.md

Read README.md for any relevant information.

## Function arguments (positional vs keyword)

- Prefer keyword arguments for readability and API stability.
- Default to **one positional argument** — the primary subject of the operation.
- A second positional is acceptable only when both args are obvious and symmetric (e.g., `copy(src, dst)`, `multiply(x, y)`, `range(start, stop)`).
- Make all other parameters **keyword-only**. Use Python's `*` to enforce this:
  ```python
  def fetch(url, *, timeout=30, retries=3, verify_ssl=True):
  ```
- Avoid positional booleans.
- Exceptions: well-known stdlib patterns, simple value objects (coordinates/colors), and functional patterns.

<!-- bv-agent-instructions-v1 -->

---

## Beads Workflow Integration

This project uses [beads_viewer](https://github.com/Dicklesworthstone/beads_viewer) for issue tracking. Issues are stored in `.beads/` and tracked in git.

### Essential Commands

```bash
# View issues (launches TUI - avoid in automated sessions)
bv

# CLI commands for agents (use these instead)
bd ready              # Show issues ready to work (no blockers)
bd list --status=open # All open issues
bd show <id>          # Full issue details with dependencies
bd create --title="..." --type=task --priority=2 --description="..."
bd update <id> --status=in_progress
bd close <id> --reason="Completed"
bd close <id1> <id2>  # Close multiple issues at once
bd sync               # Commit and push changes
#
# Use --no-daemon with all bd commands in automated sessions.
```

### Workflow Pattern

1. **Start**: Run `bd ready` to find actionable work
2. **Claim**: Use `bd update <id> --status=in_progress`
3. **Work**: Implement the task
4. **Complete**: Use `bd close <id>`
5. **Sync**: Coordinate with the user before running `bd sync`

### Key Concepts

- **Dependencies**: Issues can block other issues. `bd ready` shows only unblocked work.
- **Priority**: P0=critical, P1=high, P2=medium, P3=low, P4=backlog (use numbers, not words)
- **Types**: task, bug, feature, epic, question, docs
- **Blocking**: `bd dep add <issue> <depends-on>` to add dependencies

### Session Protocol

**Before ending any session, coordinate with the user on this checklist:**

```bash
git status              # Check what changed
git add <files>         # Stage code changes
bd sync                 # Commit beads changes
git commit -m "..."     # Commit code
bd sync                 # Commit any new beads changes
git push                # Push to remote
```

### Best Practices

- Check `bd ready` at session start to find available work
- Update status as you work (in_progress → closed)
- If asked to start work on a beads item, immediately mark it in progress
- After marking in progress, review the bead and provide a plan of action
- When closing a bead, provide a suggested git commit message (include relevant bead IDs in parentheses)
- Create new issues with `bd create` when you discover tasks (always include a description)
- Use descriptive titles and set appropriate priority/type
- Always `bd sync` before ending session

<!-- end-bv-agent-instructions -->

## Landing the Plane (Session Completion)

**When ending a work session**, coordinate with the user on ALL steps below. The user will perform git and `bd` actions.

**MANDATORY WORKFLOW (user-driven):**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - User-owned:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
