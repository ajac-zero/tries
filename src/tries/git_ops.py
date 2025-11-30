"""Git operations for try (clone and worktree support)."""

import subprocess
from pathlib import Path
from typing import Optional


def is_git_repository(path: Path) -> bool:
    """Check if a path is a git repository."""
    try:
        subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def clone_repository(url: str, target_dir: Path) -> bool:
    """Clone a git repository to the target directory.

    Args:
        url: Git repository URL (HTTPS, SSH, or local path)
        target_dir: Target directory for the clone

    Returns:
        True if successful, False otherwise
    """
    try:
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", url, str(target_dir)],
            capture_output=True,
            check=True,
            timeout=300,  # 5 minute timeout
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def create_worktree(
    repo_path: Path,
    worktree_path: Path,
    branch: Optional[str] = None,
) -> bool:
    """Create a git worktree in the target directory.

    Args:
        repo_path: Path to the source git repository
        worktree_path: Path where the worktree should be created
        branch: Optional branch to check out (creates if doesn't exist)

    Returns:
        True if successful, False otherwise
    """
    if not is_git_repository(repo_path):
        return False

    try:
        worktree_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = ["git", "-C", str(repo_path), "worktree", "add", str(worktree_path)]
        if branch:
            cmd.append(branch)

        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            timeout=60,
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def remove_worktree(repo_path: Path, worktree_path: Path) -> bool:
    """Remove a git worktree.

    Args:
        repo_path: Path to the main git repository
        worktree_path: Path to the worktree to remove

    Returns:
        True if successful, False otherwise
    """
    if not is_git_repository(repo_path):
        return False

    try:
        subprocess.run(
            ["git", "-C", str(repo_path), "worktree", "remove", str(worktree_path)],
            capture_output=True,
            check=True,
            timeout=30,
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def get_current_repo_root() -> Optional[Path]:
    """Get the root directory of the current git repository.

    Returns:
        Path to git repo root, or None if not in a git repo
    """
    try:
        output = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return Path(output.stdout.strip())
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return None
