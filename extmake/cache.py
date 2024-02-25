import hashlib
import shutil
import string
from pathlib import Path

from appdirs import user_cache_dir

FS_SAFE = string.ascii_letters + string.digits + "_-"


def _slugify(s: str) -> str:
    slug = lambda x: x if x in FS_SAFE else "_"
    return "".join(map(slug, s))


def _checksum(path: Path) -> str:
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()


def cache_root() -> Path:
    path = Path(user_cache_dir("extmake"))
    if not path.is_dir():
        path.mkdir(parents=True)
    return path


def content_key(path: Path) -> str:
    return str(path.resolve()) + "_" + _checksum(path)


def cached_file(key: str) -> Path:
    path = cache_root() / _slugify(key)
    assert path.is_file() or not path.exists(), f"cache collision for key={key}"
    return path


def cached_dir(key: str) -> Path:
    path = cache_root() / _slugify(key)
    assert path.is_dir() or not path.exists(), f"cache collision for key={key}"
    return path


def clear_all_cache():
    shutil.rmtree(cache_root())
