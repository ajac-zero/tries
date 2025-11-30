# tries — Fresh directories for every vibe

A lightweight command-line tool for managing experimental projects and throwaway directories. Instead of scattering temporary work across your filesystem, `tries` centralizes them with auto-dating, fuzzy search, and smart recall.

Built for developers with ADHD by developers with ADHD. A Python port of [tobi/try](https://github.com/tobi/try).

## Why tries?

You know the workflow:

```bash
cd ~/Desktop
mkdir redis-test
cd redis-test
# ... do stuff ...

# 3 weeks later
find ~ -type d -name "*redis*" 2>/dev/null
# Lost in the chaos
```

With `tries`:

```bash
try redis
# → instantly jump to ~/src/tries/2025-11-30-redis (or create it)

try . my-branch
# → create a git worktree in ~/src/tries/2025-11-30-my-branch

try clone https://github.com/user/project.git
# → clone into ~/src/tries/2025-11-30-project

try
# → interactive fuzzy selector through all your experiments
```

## Features

- **Centralized storage** — All experiments live in one place (`~/src/tries` by default)
- **Auto-dating** — Directories are prefixed with `YYYY-MM-DD` for natural chronological sorting
- **Fuzzy search** — Abbreviations work: `rds` matches `redis-server`, `connpool` matches `connection-pool`
- **Recency ranking** — Recently used directories float to the top
- **Git-first** — Clone repos or create worktrees with a single command
- **Interactive TUI** — Real-time filtering with keyboard navigation (arrow keys, vim bindings)
- **Shell integration** — Works with Bash, Zsh, and Fish
- **Zero dependencies** — Pure Python with standard library only
- **Non-destructive** — You control what gets deleted

## Installation

### Install with uv

```bash
uv tool install git+https://github.com/yourusername/tries.git
```

This installs the `try` command globally and makes it available in your PATH.

### Enable shell integration

The `try` command needs shell integration to actually change directories. Add one of the following to your shell configuration file and reload your shell.

**Bash** — Add to `~/.bashrc`:
```bash
eval "$(try init bash)"
```

**Zsh** — Add to `~/.zshrc`:
```bash
eval "$(try init zsh)"
```

**Fish** — Add to `~/.config/fish/config.fish`:
```fish
try init fish | source
```

After adding the integration, reload your shell or run `exec $SHELL` to activate it.

## Usage

### Basic commands

```bash
# Browse all experiments interactively
try

# Search for "redis" or create "2025-11-30-redis" if no match
try redis

# Create a new experiment explicitly
try new my-api-test

# Clone a repository with auto-dating
try clone https://github.com/octocat/Hello-World.git

# Shorthand for clone (detects .git URLs)
try https://github.com/octocat/Hello-World.git

# Create a worktree from current repo
try . feature-branch

# Create a worktree from another repo
try ./path/to/other-repo my-worktree

# Show help
try --help
```

### Interactive selector

Press `try` or `try <query>` to launch the fuzzy selector:

```
Search: redis
↓ 2025-11-30-redis-server [95%]
  2025-11-20-redis-test [82%]
  2025-10-15-red [45%]
  2025-09-01-redistribution [30%]

↑/↓ or Ctrl-P/N to navigate | Enter to select | ESC to cancel | Ctrl-D to delete
```

**Keyboard shortcuts:**
- `↑` / `↓` — Navigate results
- `Ctrl-P` / `Ctrl-N` — Navigate (alternative)
- `j` / `k` — Navigate (vim style)
- `Enter` — Select or create
- `Backspace` — Delete search character
- `Ctrl-D` — Delete directory (asks for confirmation)
- `ESC` — Cancel

### Configuration

Set the base directory via environment variable:

```bash
export TRY_PATH=~/experiments
try new my-test  # Creates ~/experiments/2025-11-30-my-test
```

Default is `~/src/tries`.

## How it works

### Scoring algorithm

Directories are ranked by a combination of:

1. **Fuzzy match quality** (70% weight)
   - Matches must be in order: `rds` finds `redis-server` but not `dreads`
   - Contiguous matches score higher: `redisser` beats `r-e-d-i-s-s-e-r`
   - Matches at word boundaries get a boost
   
2. **Recency** (30% weight)
   - Recently accessed directories float up
   - Decay over 365 days to give older experiments a chance

3. **Name length** (bonus)
   - Shorter names win on ties (helps with abbreviations)

### Directory structure

```
~/src/tries/
├── 2025-11-30-api-tests/
├── 2025-11-28-redis-server/
├── 2025-11-20-web-scraper/
└── 2025-10-01-old-project/
```

Each directory is automatically created with the current date. Use `try new` to be explicit about naming.

## Shell integration

Print shell initialization code:

```bash
try init bash   # or zsh, fish
try init        # auto-detect shell
```

The generated function wraps `tries` so that `cd` commands work:

```bash
eval "$(try init)"
try redis  # Changes directory (via eval)
```

Without this, you'd see the `cd` command printed but wouldn't actually change directories.

## Examples

**Jumping between experiments:**

```bash
# Current: ~/projects/main
try redis
# → cd ~/src/tries/2025-11-30-redis

# Later: need something from web-server project
try web
# → cd ~/src/tries/2025-11-25-web-server
```

**Cloning and exploring:**

```bash
try clone https://github.com/django/django.git
# → clones to ~/src/tries/2025-11-30-django
# → changes directory automatically

# Play around, make changes, explore
# No need to worry about cleanup—it's timestamped
```

**Creating git worktrees:**

```bash
cd ~/src/myproject
try . feature-xyz
# → creates worktree at ~/src/tries/2025-11-30-feature-xyz
# → based on current repo
# → you can modify branches independently
```

## Project layout

```
tries/
├── src/tries/
│   ├── __init__.py
│   ├── cli.py           # Argument parsing and command dispatch
│   ├── directories.py   # Directory creation and metadata
│   ├── scoring.py       # Fuzzy matching algorithm
│   ├── shell.py         # Shell detection and integration code
│   ├── git_ops.py       # Git clone and worktree operations
│   ├── tui.py           # Interactive terminal UI (curses)
│   └── main.py          # Entry point
├── tests/               # Comprehensive test suite
├── pyproject.toml       # Package metadata
└── README.md
```

All modules use Python 3.9+ type hints and follow PEP 8 conventions.

## Development

Clone the repo and install dependencies:

```bash
git clone https://github.com/yourusername/tries.git
cd tries
uv sync
```

Run tests:

```bash
uv run pytest tests/
```

Check code style:

```bash
uv run ruff check
uv run ruff format
```

## Design principles

From the original Ruby implementation:

1. **Don't make assumptions** about the user's environment
2. **Don't require elevated privileges** (no sudo needed)
3. **Don't delete stuff** (destructive operations require explicit confirmation)
4. **Embrace chaos** while providing structure
5. **Fast startup** — load only what's needed
6. **Zero config** — sensible defaults, minimal setup

## Compatibility

- **Python:** 3.9+
- **Shells:** Bash, Zsh, Fish (with fallback for unknown shells)
- **Platforms:** Linux, macOS, Unix (anything with POSIX shells)
- **Dependencies:** None (uses Python standard library only)

## Related

- **Original:** [tobi/try](https://github.com/tobi/try) (Ruby implementation)
- **Philosophy:** "[Built for developers with ADHD by developers with ADHD](https://github.com/tobi/try#design-philosophy)"

## License

MIT

---

**Fresh directories for every vibe.** Your experiments deserve a home.
