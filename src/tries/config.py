"""Configuration management for try."""

import json
import os
from pathlib import Path
from typing import Any


CONFIG_DIR = Path.home() / ".tries"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_dir() -> Path:
    """Get the try config directory (~/.tries)."""
    return CONFIG_DIR


def get_default_experiments_dir() -> Path:
    """Get the default experiments directory."""
    return CONFIG_DIR / "experiments"


def load_config() -> dict[str, Any]:
    """Load configuration from config.json.

    Returns empty dict if config doesn't exist.
    """
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_experiments_dir() -> Path:
    """Get the experiments directory.

    Priority:
    1. TRY_PATH env var (if set)
    2. experiments_dir from config.json (if set)
    3. Default: ~/.tries/experiments
    """
    # Check env var first
    env_path = os.getenv("TRY_PATH")
    if env_path:
        return Path(env_path).expanduser()

    # Check config file
    config = load_config()
    if "experiments_dir" in config:
        return Path(config["experiments_dir"]).expanduser()

    # Default
    return get_default_experiments_dir()
