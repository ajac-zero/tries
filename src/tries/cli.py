"""Command-line interface and argument parsing for try."""

import sys
from pathlib import Path
from typing import Optional

import cyclopts

from .directories import create_experiment, get_try_path
from .git_ops import clone_repository, create_worktree
from .shell import detect_shell, generate_cd_command, generate_shell_function
from .tui import TUISelector

app = cyclopts.App(
    help="Fuzzy directory navigator for experiments. Fresh directories for every vibe."
)


@app.default
def browse(query: str = "") -> None:
    """Browse or search experiments interactively.

    Parameters
    ----------
    query : str
        Optional search query. If provided, starts the TUI with this query.
        If no matches found and user cancels, creates new directory with this name.
    """
    selector = TUISelector()
    selected_dir = selector.run(initial_query=query)

    if selected_dir:
        print(generate_cd_command(selected_dir))
        return

    # If user cancelled the TUI but provided a query, create new directory with that name
    if query:
        new_dir = create_experiment(query)
        print(generate_cd_command(new_dir))
        return

    sys.exit(1)


@app.command
def new(name: str) -> None:
    """Create a new experiment directory with today's date.

    Parameters
    ----------
    name : str
        Name for the new experiment. Will be prefixed with YYYY-MM-DD.
    """
    new_dir = create_experiment(name)
    print(generate_cd_command(new_dir))


@app.command
def clone(url: str, name: Optional[str] = None) -> None:
    """Clone a Git repository into a dated directory.

    Parameters
    ----------
    url : str
        Repository URL (HTTPS or SSH).
    name : str, optional
        Custom name for the directory. If not provided, uses the repo name.
    """
    get_try_path()

    # Determine target directory name
    if name:
        target_name = name
    else:
        # Extract repo name from URL
        repo_name = url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        target_name = repo_name

    target_dir = create_experiment(target_name)

    print(f"Cloning {url}...", file=sys.stderr)
    if clone_repository(url, target_dir):
        print(generate_cd_command(target_dir))
    else:
        print(f"Error: failed to clone {url}", file=sys.stderr)
        sys.exit(1)


@app.command
def worktree(repo: Path, name: Optional[str] = None) -> None:
    """Create a Git worktree from a repository.

    Parameters
    ----------
    repo : Path
        Path to the Git repository.
    name : str, optional
        Custom name for the worktree. If not provided, uses the repo name.
    """
    repo_path = repo.resolve()

    if not repo_path.exists():
        print("Error: invalid repository path", file=sys.stderr)
        sys.exit(1)

    if not name:
        # Use repo name as default
        name = repo_path.name

    target_dir = create_experiment(name)

    print(f"Creating worktree in {target_dir}...", file=sys.stderr)
    if create_worktree(repo_path, target_dir):
        print(generate_cd_command(target_dir))
    else:
        print("Error: failed to create worktree", file=sys.stderr)
        sys.exit(1)


@app.command
def init(shell: Optional[str] = None) -> None:
    """Print shell integration code for eval.

    Outputs shell function to be evaluated with eval to enable try integration.

    Parameters
    ----------
    shell : str, optional
        Shell name (bash, zsh, fish). Auto-detects if not provided.
    """
    detected_shell = None

    if shell:
        shell_lower = shell.lower()
        if shell_lower in ("bash", "zsh", "fish"):
            from .shell import Shell

            detected_shell = Shell[shell_lower.upper()]
    else:
        detected_shell = detect_shell()

    if detected_shell:
        code = generate_shell_function(detected_shell)
        print(code)


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        app(argv)
        return 0
    except SystemExit as e:
        # Cyclopts raises SystemExit for help/version/errors
        return e.code if isinstance(e.code, int) else 1
    except Exception:
        # Re-raise any other exceptions for debugging
        raise
