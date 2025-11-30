"""Shell detection and integration utilities."""

import os
from enum import Enum
from pathlib import Path


class Shell(Enum):
    """Supported shells."""

    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    UNKNOWN = "unknown"


def detect_shell() -> Shell:
    """Detect the current shell from environment.

    Checks SHELL env var and falls back to process detection.
    """
    shell_env = os.getenv("SHELL", "")
    if "bash" in shell_env:
        return Shell.BASH
    elif "zsh" in shell_env:
        return Shell.ZSH
    elif "fish" in shell_env:
        return Shell.FISH

    # Fallback: try to detect parent process
    try:
        parent_pid = os.getppid()
        with open(f"/proc/{parent_pid}/comm", "r") as f:
            shell_name = f.read().strip()
            if "bash" in shell_name:
                return Shell.BASH
            elif "zsh" in shell_name:
                return Shell.ZSH
            elif "fish" in shell_name:
                return Shell.FISH
    except (OSError, FileNotFoundError):
        pass

    return Shell.UNKNOWN


def quote_path(path: Path) -> str:
    """Quote a path for shell use, handling special characters."""
    path_str = str(path)
    # Use double quotes and escape special characters
    if " " in path_str or "$" in path_str or "`" in path_str:
        path_str = path_str.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{path_str}"'
    return path_str


def generate_cd_command(path: Path, shell: Shell = Shell.BASH) -> str:
    """Generate a shell command to change to the given directory.

    Args:
        path: The target directory
        shell: The shell to generate command for

    Returns:
        Shell command string
    """
    quoted = quote_path(path)
    return f"cd {quoted}"


def generate_shell_function(
    shell: Shell = Shell.BASH, try_path: Path | None = None
) -> str:
    """Generate shell integration code for the try command.

    Args:
        shell: The shell to generate code for
        try_path: Custom path to try script (for development)

    Returns:
        Shell function code
    """
    if shell == Shell.FISH:
        return _generate_fish_function(try_path)
    elif shell == Shell.ZSH:
        return _generate_zsh_function(try_path)
    else:
        return _generate_bash_function(try_path)


def _generate_bash_function(try_path: Path | None = None) -> str:
    """Generate bash shell function."""
    try_cmd = str(try_path) if try_path else "try"
    return f"""try() {{
    # Avoid recursion: use 'command' to bypass this function and call the binary
    case "$1" in
        init|clone|worktree|new)
            # These commands print shell code or configuration
            command {try_cmd} "$@"
            ;;
        "")
            # No arguments: run TUI directly without eval
            command {try_cmd}
            ;;
        *)
            # Interactive mode and queries: run and eval output
            local output
            output=$(command {try_cmd} "$@" 2>/dev/null)
            local rc=$?
            if [ $rc -eq 0 ]; then
                eval "$output"
            else
                return $rc
            fi
            ;;
    esac
}}
"""


def _generate_zsh_function(try_path: Path | None = None) -> str:
    """Generate zsh shell function."""
    try_cmd = str(try_path) if try_path else "try"
    return f"""try() {{
    # Avoid recursion: use 'command' to bypass this function and call the binary
    case "$1" in
        init|clone|worktree|new)
            # These commands print shell code or configuration
            command {try_cmd} "$@"
            ;;
        "")
            # No arguments: run TUI directly without eval
            command {try_cmd}
            ;;
        *)
            # Interactive mode and queries: run and eval output
            local output
            output=$(command {try_cmd} "$@" 2>/dev/null)
            local rc=$?
            if [ $rc -eq 0 ]; then
                eval "$output"
            else
                return $rc
            fi
            ;;
    esac
}}
"""


def _generate_fish_function(try_path: Path | None = None) -> str:
    """Generate fish shell function."""
    try_cmd = str(try_path) if try_path else "try"
    return f"""function try
    # Avoid recursion: use 'command' to bypass this function and call the binary
    switch $argv[1]
        case init clone worktree new
            command {try_cmd} $argv
        case ''
            # No arguments: run TUI directly without eval
            command {try_cmd}
        case '*'
            # Interactive mode and queries: run and eval output
            set -l output (command {try_cmd} $argv 2>/dev/null)
            set -l rc $status
            if test $rc -eq 0
                eval $output
            else
                return $rc
            end
    end
end
"""
