# Try CLI - Python Port

Python implementation of [tobi/try](https://github.com/tobi/try): a fuzzy-searchable directory manager for experiments.

**Tagline**: "Fresh directories for every vibe"

## Features

- **Fuzzy search**: Match by abbreviation (`rds` → `redis-server`)
- **Auto-dating**: Create `YYYY-MM-DD-name` directories
- **Recency scoring**: Recently accessed dirs float to top
- **Git integration**: Clone repos, create worktrees
- **Interactive TUI**: Real-time filtering, keyboard nav
- **Shell agnostic**: Works with Bash/Zsh/Fish

## Commands

```bash
try                           # Browse all
try redis                      # Jump/create
try new api                    # Create "YYYY-MM-DD-new-api"
try clone <url>               # Clone repo
try . [name]                  # Worktree from current repo
try init [path]               # Shell integration
```

## Architecture

| Module | Purpose |
|--------|---------|
| `cli.py` | Argument parsing |
| `tui.py` | Terminal UI (curses) |
| `scoring.py` | Fuzzy match + recency |
| `directories.py` | CRUD ops, metadata |
| `git_ops.py` | Clone & worktrees |
| `shell.py` | Shell detection |
| `config.py` | Configuration management |
| `main.py` | Entry point |

## Scoring Formula

```
score = (fuzzy_match × 0.7) + (recency × 0.3)
```

## Config

Configuration lives in `~/.tries/config.json` (created on first write).

Priority for experiments directory:
1. `TRY_PATH` env var (highest)
2. `experiments_dir` in `~/.tries/config.json`
3. `~/.tries/experiments` (default)

Example `config.json`:
```json
{
  "experiments_dir": "~/my-experiments"
}
```

## Standards

- **Style**: `snake_case` functions, `PascalCase` classes, type hints
- **Dependencies**: Stdlib only (preferred) or minimal (click, rich, GitPython)

## Common Commands

```bash
uv run pytest tests/      # Test
uv run ruff check         # Lint
uv run ruff format        # Format
uv add <package>          # Add dep

# Pre-commit hooks (prek)
prek list                 # Show all hooks
prek run --all-files      # Run all hooks on all files
prek run <hook-id>        # Run specific hook
```

## Commit Format

Semantic commits (enforced by pre-commit):

```
feat: add fuzzy search
fix: handle empty directories
docs: update readme
```

Scopes optional: `feat(cli): add verbose flag`

## Design Principles

1. Don't assume environment
2. No elevated privileges
3. Non-destructive (ask before delete)
4. Fast startup
5. Zero config
