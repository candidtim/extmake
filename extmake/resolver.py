import hashlib
import re
import shutil
from pathlib import Path
from typing import Iterator

from . import cache, deps

RE_INCLUDE = re.compile(r"^\s*include\s+(git=.+)\s*$")


def _resolved_cache(src: Path) -> Path:
    return cache.cached_file(key=cache.content_key(src))


def _preprocess(src: Path) -> Iterator[str]:
    """Preprocess an input file, yielding the new content line by line."""
    with open(src, "r") as f:
        for line in f:
            m = RE_INCLUDE.match(line)
            if m:
                include_spec = m.group(1)
                include_path = deps.include_path(include_spec)
                yield from _preprocess(include_path)
            else:
                yield line


def _get_resolved_makefile(src: Path) -> Path:
    """
    Given a path to an existing not-preprocessed Makefile,
    prreprocess it if necessary and return a path to a processed file.
    """
    file_cache = _resolved_cache(src)

    if not file_cache.is_file():
        with open(file_cache, "w") as f:
            for line in _preprocess(src):
                f.write(line)

    return file_cache


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


def _clear_resolved_cache(src: Path):
    file_cache = _resolved_cache(src)
    if file_cache.is_file():
        file_cache.unlink()


def clear_file_cache(src: Path):
    _clear_resolved_cache(src)
    for spec in _dependencies(src):
        deps.clear_cache(spec)


def update_cache(src: Path):
    _clear_resolved_cache(src)
    for spec in _dependencies(src):
        deps.update(spec)
