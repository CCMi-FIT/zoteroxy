import yaml

from typing import List, Set


class MissingConfigurationError(Exception):

    def __init__(self, missing: List[str]):
        self.missing = missing


class SettingsConfig:

    def __init__(self, tags: frozenset, cache_duration: int):
        self.tags = tags
        self.cache_duration = cache_duration


class LibraryConfig:

    def __init__(self, library_type: str, library_id: str, name: str):
        self.type = library_type
        self.id = library_id
        self.name = name


class ZoteroConfig:

    def __init__(self, api_key: str):
        self.api_key = api_key


class ZoteroxyConfig:

    def __init__(self, zotero: ZoteroConfig, library: LibraryConfig, settings: SettingsConfig):
        self.zotero = zotero
        self.library = library
        self.settings = settings


class ZoteroxyConfigParser:

    DEFAULTS = {
        'zotero': {},
        'library': {
            'type': 'group'
        },
        'settings': {
            'tags': frozenset(),
            'cache': {
                'duration': 3600,
            },
        },
    }

    REQUIRED = [
        ['zotero', 'api_key'],
        ['library', 'id'],
        ['library', 'name'],
    ]

    def __init__(self):
        self.cfg = dict()

    def has(self, *path):
        x = self.cfg
        for p in path:
            if not hasattr(x, 'keys') or p not in x.keys():
                return False
            x = x[p]
        return True

    def _get_default(self, *path):
        x = self.DEFAULTS
        for p in path:
            x = x[p]
        return x

    def get_or_default(self, *path):
        x = self.cfg
        for p in path:
            if not hasattr(x, 'keys') or p not in x.keys():
                return self._get_default(*path)
            x = x[p]
        return x

    def validate(self):
        missing = []
        for path in self.REQUIRED:
            if not self.has(*path):
                missing.append('.'.join(path))
        if len(missing) > 0:
            raise MissingConfigurationError(missing)

    @property
    def library(self):
        return LibraryConfig(
            library_type=self.get_or_default('library', 'type'),
            library_id=self.get_or_default('library', 'id'),
            name=self.get_or_default('library', 'name'),
        )

    @property
    def settings(self):
        return SettingsConfig(
            tags=frozenset(self.get_or_default('settings', 'tags')),
            cache_duration=self.get_or_default('settings', 'cache', 'duration'),
        )

    @property
    def zotero(self):
        return ZoteroConfig(
            api_key=self.get_or_default('zotero', 'api_key'),
        )

    def parse_file(self, fp):
        self.cfg = yaml.full_load(fp)
        self.validate()
        return ZoteroxyConfig(
            zotero=self.zotero,
            library=self.library,
            settings=self.settings,
        )