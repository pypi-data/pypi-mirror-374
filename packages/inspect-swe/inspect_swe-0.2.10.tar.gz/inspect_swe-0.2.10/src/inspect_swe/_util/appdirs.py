from pathlib import Path

from inspect_ai._util.constants import PKG_NAME
from platformdirs import user_cache_path, user_data_path


def package_data_dir(subdir: str | None) -> Path:
    data_dir = user_data_path(PKG_NAME)
    if subdir:
        data_dir = data_dir / subdir
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def package_cache_dir(subdir: str | None) -> Path:
    cache_dir = user_cache_path(PKG_NAME)
    if subdir:
        cache_dir = cache_dir / subdir
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
