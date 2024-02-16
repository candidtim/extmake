import hashlib
import re
import shutil
from pathlib import Path
from typing import Iterator

from appdirs import user_cache_dir

from . import git

RE_INCLUDE = re.compile(r"^\s*#include\s+\"(.+)\"\s*$")
RE_SPEC_REMOTE = re.compile(r"^(.+)/(.+)@(.+)$")


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


def _github_clone(spec: str) -> Path:
    """
    Get the local path to the repository specified by the remote spec.
    Will clone, pull and checkout, if necessary.
    """
    m = RE_SPEC_REMOTE.match(spec)
    if not m:
        # FIXME: dedicated error class (UsageError?)
        raise ValueError(f"Invalid remote spec: {spec}")

    vendor = m.group(1)
    name = m.group(2)
    version = m.group(3)

    # ensure the repository is cloned and up to date:
    clone_dir = Path(user_cache_dir("extmake")) / _string_hash(spec)
    if not clone_dir.is_dir():
        clone_dir.parent.mkdir(parents=True, exist_ok=True)
        url = f"git@github.com:{vendor}/{name}.git"
        git.clone(url, clone_dir)
    elif not git.commit_exists(clone_dir, version):
        git.pull(clone_dir)

    # FIXME: If the user refers to a branch, it may be outdated.
    #        But, pulling every time is bad for performance.
    #        Consider adding a command to update the clones?
    #        Presently, the only option is for the user to clear the cache.

    # ensure the repository is at the right version:
    if not version in git.current_commit(clone_dir):
        git.checkout(clone_dir, version)

    return clone_dir


def _get_included_file_path(spec: str) -> Path:
    """
    Given an include spec, find the local file with the content to include.
    Specs that refer to the remote locations will be ensured locally first.
    """
    local_path = Path(spec)
    if local_path.is_file():
        return local_path

    clone_dir = _github_clone(spec)
    return clone_dir / "Makefile"


def _get_include_content(spec: str) -> Iterator[str]:
    """Given an include spec, yields ist content line by line."""
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
                yield "\n"  # avoid syntax errors due to missing newline
                yield from _get_include_content(include_spec)
                yield "\n"  # avoid syntax errors due to missing newline
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


def resolve_makefile() -> Path:
    src = Path("Makefile")
    if src.is_file():
        return _get_resolved_makefile(src)
    else:
        # that's right, return this path and let make complain properly:
        return src


def clear_cache():
    cache = Path(user_cache_dir("extmake"))
    if cache.is_dir():
        shutil.rmtree(cache)
