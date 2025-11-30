# Tries — On-demand project directories

A command-line tool for managing experimental projects. Centralizes temporary work with auto-dating, fuzzy search, and git integration. Originally a python port of [tobi/try](https://github.com/tobi/try).

## The problem

```bash
cd ~/Desktop && mkdir rds-test && cd rds-test
# ... do stuff ...

# 3 weeks later: where did it go?
find ~ -type d -name "*redis*" 2>/dev/null  # Lost in the chaos
```

## The solution

```bash
try redis                    # Jump to ~/.tries/experiments/2025-11-30-redis (create if missing)
# ... do stuff ...

# 3 weeks later...           # Fuzzy match ~/.tries/experiments/2025-11-30-redis !
try rd 
```

## Features

- **Centralized** — All experiments in `~/.tries/experiments` (configurable)
- **Auto-dated** — `YYYY-MM-DD-name` format for chronological sorting
- **Fuzzy search** — `rds` matches `redis-server`, `connpool` matches `connection-pool`
- **Recency ranking** — Recently used dirs float to top
- **Git-first** — Clone repos or create worktrees seamlessly
- **Templates** — Register reusable project scaffolds (remote or local)
- **Dashboard** — `try stats` shows disk usage, oldest/newest, top experiments
- **Interactive TUI** — Real-time filtering, keyboard nav
- **Shell integration** — Works with Bash/Zsh/Fish (enables `cd` on selection)
- **Configuration** — `~/.tries/config.json` for experiments dir, templates, etc.
- **Non-destructive** — You control deletions

## Quick start

### Install

```bash
uv tool install tries
```

### Enable shell integration

Add to `~/.bashrc` or `~/.zshrc`:
```bash
eval "$(try init)"
```

Fish:
```fish
try init fish | source
```

Then reload your shell.

## Usage

```bash
try                              # Browse all experiments
try redis                         # Jump/create redis project
try new feature-xyz              # Create "YYYY-MM-DD-feature-xyz"
try new api --template python    # Create with template
try clone <repo-url>             # Clone into dated directory
try . [name]                     # Create worktree from current repo
try stats                        # Show dashboard (size, count, oldest/newest)
try template list                # List registered templates
try template add python --url <url>  # Register remote template
try template add local --path ~/templates/my-template  # Register local template
try --help                       # Show help
```

### In the TUI

```
Search: redis
↓ 2025-11-30-redis-server [95%]
  2025-11-20-redis-test [82%]
```

Keys: `↑/↓` navigate, `Enter` select, `Ctrl-D` delete, `ESC` cancel

## Configuration

Experiments are stored in `~/.tries/experiments` by default. Customize via `~/.tries/config.json`:

```json
{
  "experiments_dir": "~/my-experiments",
  "templates": {
    "python": {
      "url": "https://github.com/user/python-template"
    },
    "nextjs": {
      "path": "~/templates/nextjs"
    }
  }
}
```

**Priority for experiments directory:**
1. `TRY_PATH` env var (if set)
2. `experiments_dir` in config.json
3. Default: `~/.tries/experiments`

## Development

```bash
git clone https://github.com/ajac-zero/try.git && cd try
uv sync
uv run pytest tests/
uv run ruff check && uv run ruff format
```
