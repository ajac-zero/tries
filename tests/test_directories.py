"""Tests for directory management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from tries.directories import (
    get_try_path,
    get_all_experiments,
    create_experiment,
    touch_experiment,
)


def test_default_try_path():
    """Default path should be ~/src/tries."""
    # Remove TRY_PATH but keep HOME/USERPROFILE for Path.home()
    with patch.dict("os.environ", {}, clear=False):
        os.environ.pop("TRY_PATH", None)
        path = get_try_path()
        expected = Path.home() / "src" / "tries"
        assert path == expected


def test_custom_try_path():
    """TRY_PATH env var should override default."""
    with patch.dict("os.environ", {"TRY_PATH": "/tmp/custom"}):
        path = get_try_path()
        assert path == Path("/tmp/custom")


def test_try_path_expansion():
    """Paths with ~ should be expanded."""
    with patch.dict("os.environ", {"TRY_PATH": "~/custom/tries"}):
        path = get_try_path()
        assert path == Path.home() / "custom" / "tries"


def test_create_experiment():
    """Creating an experiment should create dated directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict("os.environ", {"TRY_PATH": tmpdir}):
            path = create_experiment("test-project")

            # Should exist
            assert path.exists()
            assert path.is_dir()

            # Should have date prefix
            assert path.name.startswith("2025-")
            assert "test-project" in path.name


def test_create_experiment_without_name():
    """Creating experiment without name should use date only."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict("os.environ", {"TRY_PATH": tmpdir}):
            path = create_experiment("")

            assert path.exists()
            assert path.name.startswith("2025-")


def test_idempotent_creation():
    """Creating same experiment twice should work."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict("os.environ", {"TRY_PATH": tmpdir}):
            path1 = create_experiment("test-idempotent")
            # Modify something to check it's the same dir
            test_file = path1 / "test.txt"
            test_file.write_text("test")

            path2 = create_experiment("test-idempotent")

            # Same path, file should still exist
            assert path1 == path2
            assert (path2 / "test.txt").exists()


def test_get_all_experiments():
    """Should list all experiment directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict("os.environ", {"TRY_PATH": tmpdir}):
            # Create some experiments
            create_experiment("test1")
            create_experiment("test2")

            experiments = get_all_experiments()

            assert len(experiments) == 2
            names = {e.name for e in experiments}
            assert any("test1" in n for n in names)
            assert any("test2" in n for n in names)


def test_experiments_sorted_by_recency():
    """Experiments should be sorted by modification time (newest first)."""
    import time

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict("os.environ", {"TRY_PATH": tmpdir}):
            path1 = create_experiment("older")
            time.sleep(0.01)  # Ensure distinct mtime across all filesystems
            path2 = create_experiment("newer")

            experiments = get_all_experiments()

            # Newer should come first
            assert experiments[0].name == path2.name
            assert experiments[1].name == path1.name


def test_empty_try_path():
    """Non-existent try path should return empty list."""
    with patch.dict("os.environ", {"TRY_PATH": "/nonexistent/path"}):
        experiments = get_all_experiments()
        assert experiments == []


def test_touch_updates_mtime():
    """Touch should update modification time."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test"
        path.mkdir()

        original_mtime = path.stat().st_mtime

        # Wait a bit and touch
        import time

        time.sleep(0.1)
        touch_experiment(path)

        new_mtime = path.stat().st_mtime
        assert new_mtime > original_mtime
