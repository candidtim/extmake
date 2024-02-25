import hashlib
import re
import shutil
from pathlib import Path
from typing import Iterator

from . import dsn, git
from .cache import cached_dir, cached_file, content_key

RE_INCLUDE = re.compile(r"^\s*include\s+(git=.+)\s*$")


def _git_clone(url: str, rev: str) -> Path:
    """
    Get the local path to the clone of the specified repository.
    Will clone, pull and checkout, if necessary.
    """
    # ensure the repository is cloned and up to date:
    clone_dir = cached_dir(key=url)
    if not clone_dir.is_dir():
        git.clone(url, clone_dir)
    elif not git.commit_exists(clone_dir, rev):
        git.pull(clone_dir)

    # ensure the repository is at the right version:
    if rev not in git.current_commit(clone_dir):
        git.checkout(clone_dir, rev)

    return clone_dir


def _get_included_file_path(spec: str) -> Path:
    """
    Given an include spec, find the local file with the content to include.
    Specs that refer to the remote locations will be ensured locally first.
    """
    spec_kv = dsn.parse(spec)
    clone_dir = _git_clone(spec_kv["git"], spec_kv.get("rev", "master"))
    return clone_dir / spec_kv.get("path", "Makefile")


def _preprocess(src: Path) -> Iterator[str]:
    """Preprocess an input file, yielding the new content line by line."""
    with open(src, "r") as f:
        for line in f:
            m = RE_INCLUDE.match(line)
            if m:
                include_spec = m.group(1)
                include_path = _get_included_file_path(include_spec)
                yield from _preprocess(include_path)
            else:
                yield line


def _get_resolved_makefile(src: Path) -> Path:
    """
    Given a path to an existing not-preprocessed Makefile,
    prreprocess it if necessary and return a path to a processed file.
    """
    cache = cached_file(key=content_key(src))

    if not cache.is_file():
        with open(cache, "w") as f:
            for line in _preprocess(src):
                f.write(line)

    return cache


def resolve_makefile(src: Path) -> Path:
    if src.is_file():
        return _get_resolved_makefile(src)
    else:
        # that's right, return this path and let make complain properly:
        return src


def _dependencies(src: Path) -> Iterator[str]:
    with open(src, "r") as f:
        for line in f:
            m = RE_INCLUDE.match(line)
            if m:
                include_spec = m.group(1)
                include_path = _get_included_file_path(include_spec)
                yield from _dependencies(include_path)
                yield inlude_spec


def clear_file_cache(src: Path):
    src = Path("Makefile")
    cache = cached_file(key=content_key(src))
    if cache.is_file():
        cache.unlink()
    for spec in _dependencies(src):
        spec_kv = dsn.parse(spec)
        clone_dir = cached_dir(key=spec_kv["git"])
        if clone_dir.is_dir():
            shutil.rmtree(clone_dir)


def update_cache(src: Path):
    cache = cached_file(key=content_key(src))
    if cache.is_file():
        cache.unlink()
    for spec in _dependencies(src):
        spec_kv = dsn.parse(spec)
        clone_dir = cached_dir(key=spec_kv["git"])
        if clone_dir.is_dir():
            git.pull(clone_dir)
            rev = spec_kv.get("rev", "master")
            if rev not in git.current_commit(clone_dir):
                git.checkout(clone_dir, rev)
