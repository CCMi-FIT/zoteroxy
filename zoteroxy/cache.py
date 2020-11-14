import datetime
import pathlib

from typing import Any, Dict, Optional


class CachedValue:

    def __init__(self, value: Any):
        self.cached_at = datetime.datetime.now()
        self.value = value

    @property
    def age(self) -> float:
        now = datetime.datetime.now()
        return (now - self.cached_at).total_seconds()


class Cache:

    def __init__(self, duration: int):
        self._values = {}  # type: Dict[str, CachedValue]
        self.duration = duration

    def set(self, key: str, value: Any):
        self._values[key] = CachedValue(value=value)

    def has(self, key: str) -> bool:
        return key in self._values.keys()

    def is_valid(self, key: str) -> bool:
        return self.has(key) and self._values[key].age < self.duration

    def get_value(self, key: str) -> Optional[Any]:
        if key in self._values.keys():
            return self._values[key].value
        return None

    def get(self, key: str, callback=None) -> Optional[Any]:
        if key in self._values.keys():
            v = self._values[key]
            if v.age < self.duration:
                return v.value
            else:
                self._values.pop(key)
        if callable(callback):
            v = callback(key)
            self.set(key, v)
            return v
        return None

    def clear(self):
        self._values.clear()


class FileCache:

    def __init__(self, duration: int, directory: pathlib.Path):
        self._cache = Cache(duration=duration)
        self.directory = directory
        self._clear_directory()

    def _clear_directory(self):
        if self.directory.exists():
            for child in self.directory.glob('*'):
                if child.is_file():
                    child.unlink()
        else:
            self.directory.mkdir(parents=True)

    def set(self, key: str, data: bytes):
        filepath = self.directory / key
        with open(filepath, mode='wb') as f:
            f.write(data)
        self._cache.set(key, filepath)

    def get(self, key: str, callback=None) -> Optional[bytes]:
        if self._cache.has(key):
            filepath = self._cache.get_value(key)
            if self._cache.is_valid(key):
                data = filepath.read_bytes()
                return data
            else:
                filepath.unlink(missing_ok=True)
        if callable(callback):
            v = callback(key)
            self.set(key, v)
            return v
        return None

    def clear(self):
        self._clear_directory()
        self._cache.clear()
