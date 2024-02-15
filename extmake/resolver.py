import hashlib
import re
from pathlib import Path
from typing import Iterator

from appdirs import user_cache_dir

RE_INCLUDE = re.compile(r"^\s*#include\s+\"(.+)\"\s*$")


def _path_hash(path: Path) -> str:
    """MD5 hash of the absolute path of a given argument"""
    md5 = hashlib.md5()
    md5.update(str(path.resolve()).encode("utf-8"))
    return md5.hexdigest()


def _get_included_file_path(spec: str) -> Path:
    """
    Given an include spec, find the local file with the content to include.
    Specs that refer to the remote locations will be ensured locall first.
    """
    local_path = Path(spec)
    if local_path.is_file():
        return local_path

    raise NotImplementedError(f"Remote includes are not supported yet")


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
    cache = Path(user_cache_dir("extmake")) / _path_hash(src)

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
