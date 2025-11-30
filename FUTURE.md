# Future Ideas

Ideas for improving the `try` package, organized by category.

## Core Features

- [ ] **Tagging/categorization** — Add optional tags (`try redis --tag database`) to group experiments beyond just date. Filter/search by tags in TUI.
- [ ] **Quick notes** — Store brief context with each directory (`try new feature-x --note "testing oauth"`) displayable in TUI results.
- [ ] **Directory templates** — Clone a template structure into new experiments (Python venv, Docker compose, npm setup, etc).

## Scoring & Discovery

- [ ] **Custom weights** — Let users adjust fuzzy/recency balance in config for their workflow.
- [ ] **Search history** — Log previous searches to autocomplete or show frequently-used patterns.
- [ ] **Suggestions on empty search** — Show trending/recently-created rather than all dirs when no query.

## Usability

- [ ] **Open in editor** — Add `Ctrl+O` in TUI to open directory in `$EDITOR` or `code`/`vim` directly.
- [ ] **Export/archive** — Move old experiments to archive directory with `try archive` without losing them.
- [ ] **Stats dashboard** — Show experiment counts, oldest, newest, most-used, disk usage.
- [ ] **Soft delete/restore** — Move to trash instead of direct deletion, with restore option.

## Integration

- [ ] **GitHub clone defaults** — Expand `try clone` to handle `org/repo` shorthand automatically.
- [ ] **Symlink management** — Auto-symlink latest matching experiment to `~/src/tries/latest`.
- [ ] **Python venv auto-activation** — Detect and auto-source venv in new experiment directory.

## Technical

- [ ] **Async git operations** — Make clone/worktree non-blocking for better TUI responsiveness.
- [ ] **Import/export config** — Backup and share experiment lists with teammates.
- [ ] **Database instead of filesystem traversal** — SQLite backend for faster searches on large directories.
