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


def current_commit(clone: Path) -> list[str]:
    """
    Get the list of identifiers describing the current commit.
    At the very least, it should contain the short and long hash of the commit.
    It may also contain the branch name and the tag name.
    The list may be not exhaustive (only most recent tag, only current branch, etc.)
    """
    commit_ids = []

    def _get_commit_id(*args: str, optional: bool = False) -> str:
        res = _git(clone, *args, check=not optional)
        if res.returncode == 0:
            commit_ids.append(res.stdout.decode("utf-8").strip())

    _get_commit_id("rev-parse", "--short", "HEAD")
    _get_commit_id("rev-parse", "HEAD")
    _get_commit_id("symbolic-ref", "--short", "HEAD", optional=True)
    _get_commit_id("symbolic-ref", "HEAD", optional=True)
    _get_commit_id("describe", "--tags", "--exact-match", "HEAD", optional=True)

    return commit_ids


def checkout(clone: Path, commit: str) -> None:
    """Checkout the given commit."""
    _git(clone, "checkout", commit)
