import logging
import shutil
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

    # ensure the repository is cloned:
    if not clone_dir.is_dir():
        logging.debug(f"Cloning {url} to {clone_dir}")
        git.clone(url, clone_dir)

    # and up to date:
    elif not git.commit_exists(clone_dir, rev):
        logging.debug(f"Pulling {url} in {clone_dir}")
        git.pull(clone_dir)

    else:
        logging.debug(f"Clone for {url} already exists and up to date")

    # ensure the repository is at the right version (no-op if already there):
    logging.debug(f"Checking out {rev} in {clone_dir}")
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
    logging.debug(f"Pulling {spec.git} in {clone_dir}")
    git.pull(clone_dir)
    logging.debug(f"Checking out {rev} in {clone_dir}")
    git.checkout(clone_dir, spec.rev)


def clear_cache(dsn_spec: str):
    """Delete the cache associated with the given dependency."""
    spec = _parse_spec(dsn_spec)
    clone_dir = cache.cached_dir(key=spec.git)
    if clone_dir.is_dir():
        logging.debug(f"Removing cached {clone_dir}")
        shutil.rmtree(clone_dir)
    else:
        logging.debug(f"No cache found for {spec.git}")
