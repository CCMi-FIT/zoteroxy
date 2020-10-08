import datetime
from pyzotero import zotero

from typing import Dict, List

from zoteroxy.config import ZoteroxyConfig
from zoteroxy.model import LibraryItem, AttachmentMetadata


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

    def _tags_allowed(self, tags):
        for t in tags:
            if t in self.config.settings.tags:
                return True
        return False

    def attachment_metadata(self, key) -> AttachmentMetadata:
        # TODO: cache
        item = self.library.item(key)
        if item['data']['itemType'] != 'attachment':
            raise RuntimeError('Not an attachment')
        if not self._tags_allowed(item['data']['tags']):
            raise RuntimeError('Not allowed attachment')
        return AttachmentMetadata(item)

    def attachment_data(self, metadata: AttachmentMetadata) -> bytes:
        # TODO: cache
        data = self.library.file(metadata.key)
        return data

    def _items(self):
        # TODO: query children attachments (for multiple)
        return self.library.items(tag=self.config.settings.tags)

    def items(self) -> List[LibraryItem]:
        result = self._from_cache('items')
        if result is None:
            result = self._items()
            self.cache['items'] = CachedValue(result)
        return [LibraryItem(item) for item in result]
