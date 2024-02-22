import hashlib
import re
import shutil
from pathlib import Path
from typing import Iterator

from appdirs import user_cache_dir

from . import dsn, git

RE_INCLUDE = re.compile(r"^\s*include\s+(git=.+)\s*$")


def _string_hash(s: str) -> str:
    """MD5 hash of a given string"""
    md5 = hashlib.md5()
    md5.update(s.encode("utf-8"))
    return md5.hexdigest()


def _file_hash(path: Path) -> str:
    """MD5 hash of the given file content"""
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()


def _git_clone(url: str, rev: str) -> Path:
    """
    Get the local path to the clone of the specified repository.
    Will clone, pull and checkout, if necessary.
    """
    # ensure the repository is cloned and up to date:
    clone_dir = Path(user_cache_dir("extmake")) / _string_hash(url)
    if not clone_dir.is_dir():
        clone_dir.parent.mkdir(parents=True, exist_ok=True)
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


def _get_include_content(spec: str) -> Iterator[str]:
    """Given an include spec, yields its content line by line."""
    include_path = _get_included_file_path(spec)
    with open(include_path, "r") as f:
        yield from f


def _preprocess(src: Path) -> Iterator[str]:
    """Preprocess an input file, yielding the new content line by line."""
    with open(src, "r") as f:
        for line in f:
            m = RE_INCLUDE.match(line)
            if m:
                include_spec = m.group(1)
                yield from _get_include_content(include_spec)
            else:
                yield line


def _get_resolved_makefile(src: Path) -> Path:
    """
    Given a path to an existing not-preprocessed Makefile,
    prreprocess it if necessary and return a path to a processed file.
    """
    cache = Path(user_cache_dir("extmake")) / _file_hash(src)

    if not cache.is_file():
        cache.parent.mkdir(parents=True, exist_ok=True)
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
                yield m.group(1)


def clear_file_cache(src: Path):
    src = Path("Makefile")
    cache = Path(user_cache_dir("extmake")) / _file_hash(src)
    if cache.is_file():
        cache.unlink()
    for spec in _dependencies(src):
        spec_kv = dsn.parse(spec)
        clone_dir = Path(user_cache_dir("extmake")) / _string_hash(spec_kv["git"])
        if clone_dir.is_dir():
            shutil.rmtree(clone_dir)


def update_cache(src: Path):
    cache = Path(user_cache_dir("extmake")) / _file_hash(src)
    if cache.is_file():
        cache.unlink()
    for spec in _dependencies(src):
        spec_kv = dsn.parse(spec)
        clone_dir = Path(user_cache_dir("extmake")) / _string_hash(spec_kv["git"])
        if clone_dir.is_dir():
            git.pull(clone_dir)
            rev = spec_kv.get("rev", "master")
            if rev not in git.current_commit(clone_dir):
                git.checkout(clone_dir, rev)


def clear_all_cache():
    cache = Path(user_cache_dir("extmake"))
    if cache.is_dir():
        shutil.rmtree(cache)
