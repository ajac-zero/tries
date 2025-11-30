# try — Fresh directories for every vibe

A command-line tool for managing experimental projects. Centralizes temporary work with auto-dating, fuzzy search, and git integration. Python port of [tobi/try](https://github.com/tobi/try).

## The problem

```bash
cd ~/Desktop && mkdir redis-test && cd redis-test
# ... do stuff ...

# 3 weeks later: where did it go?
find ~ -type d -name "*redis*" 2>/dev/null  # Lost in the chaos
```

## The solution

```bash
try redis                    # Jump to ~/src/tries/2025-11-30-redis (create if missing)
try new api-test             # Explicit creation
try .                        # Create git worktree from current repo
try clone <url>              # Clone into dated directory
try                          # Interactive fuzzy selector
```

## Features

- **Centralized** — All experiments in `~/src/tries` (configurable via `TRY_PATH`)
- **Auto-dated** — `YYYY-MM-DD-name` format for chronological sorting
- **Fuzzy search** — `rds` matches `redis-server`, `connpool` matches `connection-pool`
- **Recency ranking** — Recently used dirs float to top
- **Git-first** — Clone repos or create worktrees seamlessly
- **Interactive TUI** — Real-time filtering, keyboard nav
- **Shell integration** — Works with Bash/Zsh/Fish (enables `cd` on selection)
- **Zero dependencies** — Standard library only
- **Non-destructive** — You control deletions

## Quick start

### Install

```bash
uv tool install git+https://github.com/ajac-zero/try.git
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
try                      # Browse all experiments
try redis                # Jump/create redis project
try new feature-xyz      # Create "YYYY-MM-DD-feature-xyz"
try clone <repo-url>     # Clone into dated directory
try . [name]             # Create worktree from current repo
try --help               # Show help
```

### In the TUI

```
Search: redis
↓ 2025-11-30-redis-server [95%]
  2025-11-20-redis-test [82%]
```

Keys: `↑/↓` navigate, `Enter` select, `Ctrl-D` delete, `ESC` cancel

## How scoring works

```
score = (fuzzy_match × 0.7) + (recency × 0.3)
```

- **Fuzzy match** (70%): Quality of your search match
- **Recency** (30%): How recently you accessed it

## Design principles

1. No environment assumptions
2. No elevated privileges
3. Non-destructive by default
4. Fast startup
5. Zero config (sensible defaults)

## Development

```bash
git clone https://github.com/ajac-zero/try.git && cd try
uv sync
uv run pytest tests/
uv run ruff check && uv run ruff format
```

---

**Built for developers with ADHD by developers with ADHD.** Your experiments deserve a home.
