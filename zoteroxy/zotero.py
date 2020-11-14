from pyzotero import zotero

from typing import List

from zoteroxy.cache import Cache, FileCache
from zoteroxy.config import ZoteroxyConfig
from zoteroxy.model import LibraryItem, Collection, Attachment


class Zotero:

    def __init__(self, config: ZoteroxyConfig):
        self.config = config
        self._metadata_cache = Cache(duration=config.settings.cache_duration)
        self._file_cache = FileCache(duration=config.settings.cache_file_duration,
                                     directory=config.settings.cache_directory)
        self.library = zotero.Zotero(config.library.id, config.library.type, config.zotero.api_key)

    def _tags_allowed(self, tags) -> bool:
        return any(map(lambda t: t in self.config.settings.tags, tags))

    def attachment_metadata(self, key) -> Attachment:
        item = self._metadata_cache.get(key=f'item_{key}', callback=lambda k: self.library.item(key))
        if item['data']['itemType'] != 'attachment':
            raise RuntimeError('Not an attachment')
        metadata = Attachment(item)
        if not self._tags_allowed(metadata.tags):
            raise RuntimeError('Not allowed attachment')
        return metadata

    def attachment_data(self, metadata: Attachment) -> bytes:
        file_key = f'{metadata.key}_{metadata.file_hash}'
        data = self._file_cache.get(file_key, callback=lambda k: self.library.file(metadata.key))
        return data

    def _items(self) -> dict:
        items_dict = dict()
        items_list = self.library.everything(
            self.library.items(tag=self.config.settings.tags)
        )  # type: List[dict]
        for item in items_list:
            key = item.get('key', None)
            data = item.get('data', dict())
            item_type = data.get('itemType', None)
            if key is None or item_type is None:
                continue
            items_dict[key] = item
            items_dict[key]['children'] = list()
        for key, item in items_dict.items():
            parent_key = item['data'].get('parentItem', None)
            if parent_key is not None and parent_key in items_dict.keys():
                items_dict[parent_key]['children'].append(item)
        return items_dict

    @property
    def items(self) -> List[LibraryItem]:
        result = self._metadata_cache.get(key='items', callback=lambda k: self._items())  # type: dict
        items = (LibraryItem(item) for item in result.values())
        return [i for i in items if i.type != 'attachment']

    @property
    def collection(self):
        return Collection(
            items=self.items,
            config=self.config
        )

    def clear_cache(self):
        self._metadata_cache.clear()
        self._file_cache.clear()
