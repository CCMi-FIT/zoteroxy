from pyzotero import zotero

from typing import List

from zoteroxy.cache import Cache, FileCache
from zoteroxy.config import ZoteroxyConfig
from zoteroxy.model import LibraryItem, AttachmentMetadata


class Zotero:

    def __init__(self, config: ZoteroxyConfig):
        self.config = config
        self._metadata_cache = Cache(duration=config.settings.cache_duration)
        self._file_cache = FileCache(duration=config.settings.cache_file_duration,
                                     directory=config.settings.cache_directory)
        self.library = zotero.Zotero(config.library.id, config.library.type, config.zotero.api_key)

    def _tags_allowed(self, tags) -> bool:
        return any(map(lambda t: t in self.config.settings.tags, tags))

    def attachment_metadata(self, key) -> AttachmentMetadata:
        item = self._metadata_cache.get(key=f'item_{key}', callback=lambda k: self.library.item(key))
        if item['data']['itemType'] != 'attachment':
            raise RuntimeError('Not an attachment')
        metadata = AttachmentMetadata(item)
        if not self._tags_allowed(metadata.tags):
            raise RuntimeError('Not allowed attachment')
        return metadata

    def attachment_data(self, metadata: AttachmentMetadata) -> bytes:
        file_key = f'{metadata.key}_{metadata.file_hash}'
        data = self._file_cache.get(file_key, callback=lambda k: self.library.file(metadata.key))
        return data

    def _items(self) -> list:
        # TODO: query children attachments (for multiple)
        return self.library.items(tag=' OR '.join(self.config.settings.tags))

    def items(self) -> List[LibraryItem]:
        result = self._metadata_cache.get(key='items', callback=lambda k: self._items())
        items = (LibraryItem(item) for item in result)
        return [i for i in items if i.type != 'attachment']
