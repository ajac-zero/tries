"""Directory management for try experiments."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

from .config import get_experiments_dir


def get_try_path() -> Path:
    """Get the base directory for try experiments.

    Returns the path specified by TRY_PATH env var, then config file,
    or defaults to ~/.tries/experiments.
    """
    return get_experiments_dir()


def ensure_try_directory_exists() -> Path:
    """Ensure the try base directory exists, creating if necessary."""
    try_path = get_try_path()
    try_path.mkdir(parents=True, exist_ok=True)
    return try_path


def get_all_experiments() -> list[Path]:
    """Get all experiment directories, sorted by recency (newest first)."""
    try_path = get_try_path()
    if not try_path.exists():
        return []

    try:
        experiments = [
            d for d in try_path.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]
    except (OSError, PermissionError):
        return []

    # Sort by modification time (newest first)
    return sorted(experiments, key=lambda d: d.stat().st_mtime, reverse=True)


def get_experiment_mtime(path: Path) -> float:
    """Get modification time of an experiment directory."""
    try:
        return path.stat().st_mtime
    except (OSError, FileNotFoundError):
        return 0.0


def create_experiment(name: str) -> Path:
    """Create a new experiment directory with today's date prefix.

    Args:
        name: The project name (will be prefixed with YYYY-MM-DD)

    Returns:
        Path to the newly created directory
    """
    try_path = ensure_try_directory_exists()
    today = datetime.now().strftime("%Y-%m-%d")
    dirname = f"{today}-{name}" if name else today

    new_dir = try_path / dirname
    new_dir.mkdir(exist_ok=True)

    return new_dir


def delete_experiment(path: Path, force: bool = False) -> bool:
    """Delete an experiment directory.

    Args:
        path: Path to the experiment directory
        force: If True, don't ask for confirmation

    Returns:
        True if deleted, False otherwise
    """
    if not path.exists():
        return False

    if not force:
        response = input(f"Delete {path.name}? [y/N]: ").strip().lower()
        if response != "y":
            return False

    try:
        shutil.rmtree(path)
        return True
    except (OSError, PermissionError):
        return False


def touch_experiment(path: Path) -> None:
    """Update the modification time of an experiment to mark it as accessed."""
    if path.exists():
        path.touch()


class ExperimentStats(NamedTuple):
    """Statistics for an experiment directory."""

    name: str
    path: Path
    size_bytes: int
    mtime: float


class StatsSnapshot(NamedTuple):
    """Overall statistics snapshot."""

    total_experiments: int
    total_size_bytes: int
    oldest_mtime: float
    newest_mtime: float
    experiments: list[ExperimentStats]


def get_dir_size(path: Path) -> int:
    """Get total size of a directory in bytes."""
    try:
        total = 0
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
        return total
    except (OSError, PermissionError):
        return 0


def get_experiment_stats() -> StatsSnapshot:
    """Get statistics for all experiments.

    Returns:
        StatsSnapshot with aggregate stats and per-experiment details
    """
    experiments = get_all_experiments()

    if not experiments:
        return StatsSnapshot(
            total_experiments=0,
            total_size_bytes=0,
            oldest_mtime=0.0,
            newest_mtime=0.0,
            experiments=[],
        )

    stats_list: list[ExperimentStats] = []
    total_size = 0
    mtimes = []

    for exp_path in experiments:
        size = get_dir_size(exp_path)
        mtime = get_experiment_mtime(exp_path)
        stats_list.append(ExperimentStats(exp_path.name, exp_path, size, mtime))
        total_size += size
        mtimes.append(mtime)

    return StatsSnapshot(
        total_experiments=len(experiments),
        total_size_bytes=total_size,
        oldest_mtime=min(mtimes) if mtimes else 0.0,
        newest_mtime=max(mtimes) if mtimes else 0.0,
        experiments=stats_list,
    )
