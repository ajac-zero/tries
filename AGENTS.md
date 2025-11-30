# AGENTS.md - Try CLI Python Port

## Project Overview

This project is a Python port of [tobi/try](https://github.com/tobi/try), a lightweight command-line tool for managing experimental projects and throwaway directories.

**Purpose**: Centralized, fuzzy-searchable directory navigator for developers who constantly create temporary projects. Instead of scattering experiments across the filesystem, `try` centralizes them with auto-dating and smart recall.

**Tagline**: "Fresh directories for every vibe" — Your experiments deserve a home.

## Core Features to Implement

### 1. Fuzzy Directory Search
- Intelligent matching algorithm that ranks results by:
  - **Recency**: Recently accessed directories float to top
  - **Match Quality**: Supports abbreviations (e.g., `rds` → `redis-server`)
  - **Name Length**: Shorter names win on equal matches
- Real-time filtering as user types

### 2. Directory Management
- Auto-creates timestamped directories: `YYYY-MM-DD-project-name`
- Centralized storage location: `~/src/tries` (configurable via `TRY_PATH`)
- Non-destructive operations (user controls deletion)

### 3. Git Integration
- Clone repos into date-prefixed directories: `try clone <url>`
- Create git worktrees from current repo: `try . [name]`
- Support multiple git URI formats (HTTPS GitHub, SSH, GitLab, etc.)

### 4. Terminal User Interface (TUI)
- Interactive selector with real-time filtering
- Shows last-access time for each directory
- Keyboard navigation:
  - `↑/↓` or `Ctrl-P/N/J/K`: Navigate
  - `Enter`: Select or create
  - `Backspace`: Delete character
  - `Ctrl-D`: Delete directory (with confirmation)
  - `ESC`: Cancel
- Match scoring visibility (why items are ranked that way)

### 5. Shell Integration
- Support Bash, Zsh, Fish shells
- Print shell-neutral cd commands (absolute paths, quoted)
- Shell function integration via `eval`

## Command Reference

```bash
try                                        # Browse all experiments interactively
try redis                                  # Jump to redis experiment or create new
try new api                                # Start with "2025-08-17-new-api"
try . [name]                               # Create dated worktree from current repo
try ./path/to/repo [name]                  # Use another repo as worktree source
try worktree dir [name]                    # Explicit worktree form
try clone https://github.com/user/repo.git # Clone repo into date-prefixed dir
try https://github.com/user/repo.git       # Shorthand for clone
try --help                                 # Show help
try init [path]                            # Print shell integration code
```

## Original Ruby Implementation Details

**Characteristics**:
- Single-file script (`try.rb`)
- Zero external dependencies
- ~400-500 lines of code
- Uses Ruby's built-in libraries
- Reads directory metadata (mtime) for recency

**Key Design Philosophy**:
- One file, easy to hack
- Minimal configuration needed
- Non-destructive operations
- Shell-neutral output format

## Python Implementation Strategy

### Dependencies
**Minimal approach** (preferred):
- `curses` (stdlib) for TUI
- Standard library only for file I/O, subprocess, etc.

**Enhanced approach** (if needed):
- `click` or `typer`: CLI framework
- `rich`: Better terminal UI
- `fuzzywuzzy` or custom: Fuzzy matching
- `gitpython`: Git operations

### Core Modules to Create
1. **`cli.py`**: Command-line interface and argument parsing
2. **`tui.py`**: Terminal user interface (fuzzy selector)
3. **`scoring.py`**: Fuzzy matching and recency scoring algorithm
4. **`directories.py`**: Directory management (create, list, metadata)
5. **`git_ops.py`**: Git clone and worktree operations
6. **`shell.py`**: Shell detection and integration
7. **`main.py`**: Entry point

### Key Algorithms

#### Scoring Algorithm
Combines fuzzy match score with recency:
```
final_score = (fuzzy_score * 0.7) + (recency_score * 0.3)
recency_score = 1 - (days_since_access / max_days)
```

#### Fuzzy Matching
- Support substring matching: `rds` matches `redis-server`
- Support abbreviations: `connpool` matches `connection-pool`
- Case-insensitive
- Boost recently modified directories

### Configuration
- **Default path**: `~/src/tries`
- **Override via**: `TRY_PATH` environment variable
- **No config file needed**: Single env var is sufficient

## Code Style & Structure

### File Organization
```
try/
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── cli.py           # Argument parsing
│   ├── tui.py           # Terminal UI
│   ├── scoring.py       # Fuzzy matching & scoring
│   ├── directories.py   # Directory management
│   ├── git_ops.py       # Git operations
│   └── shell.py         # Shell integration
├── tests/
├── pyproject.toml
├── README.md
└── AGENTS.md
```

### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: prefix with `_`

### Documentation
- Docstrings for all public functions
- Type hints throughout (Python 3.9+)
- Comments for complex algorithms

## Testing Strategy

- Unit tests for fuzzy matching, scoring, directory ops
- Integration tests for CLI commands
- Shell integration tests for bash/zsh/fish

## Common Agent Commands

When working on this project:

```bash
# Run tests
uv run pytest tests/

# Check code style
uv run ruff check

# Format code
uv run ruff format

# Add dependencies
uv add <package>
uv add --dev <package>  # dev dependencies

# Sync dependencies
uv sync
```

## Reference Links

- Original: https://github.com/tobi/try
- Ruby source: https://github.com/tobi/try/blob/main/try.rb
- Philosophy: "Built for developers with ADHD by developers with ADHD"

## Design Principles (from original)

1. **Don't make assumptions** about the user's environment
2. **Don't require elevated privileges** (no sudo needed)
3. **Don't delete stuff** (destructive ops require explicit confirmation)
4. **Embrace chaos** while providing structure
5. **Fast startup** - load only what's needed
6. **Zero config** - sensible defaults, minimal setup
