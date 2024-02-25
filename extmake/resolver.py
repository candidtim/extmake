import hashlib
import logging
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
        logging.debug(f"No cache found for {src}, preprocessing")
        with open(makefile, "w") as f:
            for line in _preprocess(src):
                f.write(line)
        logging.debug(f"Cached the processed {src} to {makefile}")
    else:
        logging.debug(f"Using cached {makefile}")

    return makefile


def _preprocess(src: Path) -> Iterator[str]:
    """Preprocess an input file, yielding the new content line by line."""
    for line in parser.parse(src):
        match line.TYPE:
            case parser.Dependency.TYPE:
                include_path = deps.include_path(line.spec)
                yield from _preprocess(include_path)
            case parser.RawLine.TYPE:
                yield line.raw
            case _:
                raise AssertionError(f"unknown line type: {line.TYPE}")


def dependencies(src: Path) -> Iterator[str]:
    for line in parser.parse(src):
        match line.TYPE:
            case parser.Dependency.TYPE:
                include_path = deps.include_path(line.spec)
                yield from dependencies(include_path)
                yield line.spec


def _resolved_makefile(src: Path) -> Path:
    return cache.cached_file(key=cache.content_key(src))


def clear_cache(src: Path):
    makefile = _resolved_makefile(src)
    if makefile.is_file():
        logging.debug(f"Removing cached {makefile}")
        makefile.unlink()
    else:
        logging.debug(f"No cache found for {src}")
