"""Tests for CLI commands."""

import pytest
from tries.cli import app, browse, new, clone, worktree, init


def test_app_exists():
    """App should be properly configured."""
    assert app is not None
    assert app.help is not None


def test_browse_function_exists():
    """Browse function should exist with query parameter."""
    import inspect

    sig = inspect.signature(browse)
    assert "query" in sig.parameters


def test_new_function_exists():
    """New function should exist with name parameter."""
    import inspect

    sig = inspect.signature(new)
    assert "name" in sig.parameters


def test_clone_function_exists():
    """Clone function should exist with url and optional name."""
    import inspect

    sig = inspect.signature(clone)
    assert "url" in sig.parameters
    assert "name" in sig.parameters


def test_worktree_function_exists():
    """Worktree function should exist with repo and optional name."""
    import inspect

    sig = inspect.signature(worktree)
    assert "repo" in sig.parameters
    assert "name" in sig.parameters


def test_init_function_exists():
    """Init function should exist with optional shell parameter."""
    import inspect

    sig = inspect.signature(init)
    assert "shell" in sig.parameters


def test_app_help():
    """App should have help text."""

    # Test that --help can be invoked (it will exit)
    with pytest.raises(SystemExit):
        app(["--help"])
