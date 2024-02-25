from dataclasses import dataclass
from pathlib import Path

from . import cache, dsn, git


@dataclass
class Dependency:
    git: str
    rev: str = "master"
    path: str = "Makefile"


def _parse_spec(spec: str) -> Dependency:
    kv = dsn.parse(spec)
    return Dependency(**kv)


def _get_dependency_clone(url: str, rev: str) -> Path:
    """
    Get the local path to the clone of the specified repository.
    Will clone, pull and checkout, if necessary.
    """
    clone_dir = cache.cached_dir(key=url)

    # ensure the repository is cloned and up to date:
    if not clone_dir.is_dir():
        git.clone(url, clone_dir)

    # otherwise, ensure the repository is up to date:
    # (will pull if the user changed the revision,
    #  but will not pull if the revision is a branch and didn't change)
    elif not git.commit_exists(clone_dir, rev):
        git.pull(clone_dir)

    # ensure the repository is at the right version (no-op if already there):
    git.checkout(clone_dir, rev)

    return clone_dir


def include_path(dsn_spec: str) -> Path:
    """
    Obtain the given dependency (if necessary) and get the path to the
    specified include file.
    """
    spec = _parse_spec(dsn_spec)
    clone_dir = _get_dependency_clone(spec.git, spec.rev)
    return clone_dir / spec.path


def update(dsn_spec: str):
    """Update the local copy of the given dependency."""
    spec = _parse_spec(dsn_spec)
    clone_dir = _get_dependency_clone(spec.git, spec.rev)
    git.pull(clone_dir)
    git.checkout(clone_dir, spec.rev)


def clear_cache(dsn_spec: str):
    """Delete the cache associated with the given dependency."""
    spec = _parse_spec(dsn_spec)
    clone_dir = cache.cached_dir(key=spec.git)
    if clone_dir.is_dir():
        shutil.rmtree(clone_dir)
