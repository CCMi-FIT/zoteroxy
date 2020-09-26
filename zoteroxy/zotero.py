import datetime
from pyzotero import zotero

from typing import Dict

from zoteroxy.config import ZoteroxyConfig


class CachedValue:

    def __init__(self, value):
        self.cached_at = datetime.datetime.now()
        self.value = value

    @property
    def age(self):
        now = datetime.datetime.now()
        return (now - self.cached_at).total_seconds()


class Zotero:

    def __init__(self, config: ZoteroxyConfig):
        self.config = config
        self.cache = {}  # type: Dict[str, CachedValue]
        self.library = zotero.Zotero(config.library.id, config.library.type, config.zotero.api_key)

    def _from_cache(self, key: str):
        if key not in self.cache.keys():
            return None
        if self.cache[key].age > 300:
            return None
        return self.cache[key].value

    def _items(self):
        return self.library.items(tag=self.config.settings.tags)

    def items(self):
        # TODO: reformat items
        result = self._from_cache('items')
        if result is None:
            result = self._items()
            self.cache['items'] = CachedValue(result)
        return result
