"""Simple wrapper for some git commands."""

# FIXME: consider using GitPython if this goes too far

import subprocess
from pathlib import Path


class FatalGitError(Exception):
    """An error that cannot be recovered from."""

    pass


def _git(workdir: Path, *args: str, check: bool = True) -> str:
    """Run a git command and return the output."""
    try:
        return subprocess.run(["git", *args], cwd=workdir, check=check, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise FatalGitError(f"'git {' '.join(args)}' failed") from e


def clone(url: str, path: Path) -> None:
    """Clone a git repository to a given path."""
    _git(path.parent, "clone", url, str(path))


def pull(clone: Path) -> None:
    """Pull the latest changes for the repository at the given path."""
    res = _git(clone, "pull")


def commit_exists(clone: Path, commit: str) -> bool:
    """Check if the given commit exists in the repository."""
    res = _git(clone, "rev-parse", "--quiet", "--verify", commit, check=False)
    return res.returncode == 0


def checkout(clone: Path, commit: str) -> None:
    """Checkout the given commit."""
    _git(clone, "checkout", commit)
