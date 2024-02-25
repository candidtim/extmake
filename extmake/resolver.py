import hashlib
import shutil
from pathlib import Path
from typing import Iterator

from . import cache, deps, parser


def resolve_makefile(src: Path) -> Path:
    """
    Given a path to an existing not-preprocessed Makefile,
    prreprocess it if necessary and return a path to a processed file.
    """
    makefile = _resolved_makefile(src)

    if not makefile.is_file():
        with open(makefile, "w") as f:
            for line in _preprocess(src):
                f.write(line)

    return makefile


def _preprocess(src: Path) -> Iterator[str]:
    """Preprocess an input file, yielding the new content line by line."""
    for line in parser.parse(src):
        if isinstance(line, parser.Dependency):
            include_path = deps.include_path(line.spec)
            yield from _preprocess(include_path)
        else:
            yield line.raw


def _dependencies(src: Path) -> Iterator[str]:
    for line in parser.parse(src):
        if isinstance(line, parser.Dependency):
            include_path = deps.include_path(line.spec)
            yield from _dependencies(include_path)
            yield inlude_spec


def _resolved_makefile(src: Path) -> Path:
    return cache.cached_file(key=cache.content_key(src))


def _clear_resolved_cache(src: Path):
    makefile = _resolved_makefile(src)
    if makefile.is_file():
        makefile.unlink()


def clear_cache(src: Path):
    _clear_resolved_cache(src)
    for spec in _dependencies(src):
        deps.clear_cache(spec)


def update_cache(src: Path):
    _clear_resolved_cache(src)
    for spec in _dependencies(src):
        deps.update(spec)
