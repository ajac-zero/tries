"""Directory management for try experiments."""

import os
import shutil
from datetime import datetime
from pathlib import Path


def get_try_path() -> Path:
    """Get the base directory for try experiments.

    Returns the path specified by TRY_PATH env var, or defaults to ~/src/tries.
    """
    env_path = os.getenv("TRY_PATH")
    if env_path:
        return Path(env_path).expanduser()
    return Path.home() / "src" / "tries"


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
