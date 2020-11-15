import datetime

from typing import List, Optional

from zoteroxy.config import ZoteroxyConfig


def extract_year(datestr: str) -> Optional[str]:
    for i in range(len(datestr)-3):
        if datestr[i:i+4].isdigit():
            return datestr[i:i+4]
    return None


def from_timestamp(timestamp: Optional[str]) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    except Exception:
        return datetime.datetime.now()


class Author:

    _AUTHOR_TYPES = frozenset(['author', 'presenter'])
    _EDITOR_TYPES = frozenset(['editor'])

    def __init__(self, data: dict):
        self.type = data.get('creatorType', 'author')
        self.firstname = data.get('firstName', None)
        self.lastname = data.get('lastName', None)
        if self.firstname is None and self.lastname is None and ' ' in data.get('name', ''):
            self.firstname, self.lastname = data['name'].split(' ', maxsplit=1)

    def serialize(self):
        return {
            'type': self.type,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'name': f'{self.firstname} {self.lastname}'
        }

    @property
    def is_author(self):
        return self.type in self._AUTHOR_TYPES

    @property
    def is_editor(self):
        return self.type in self._EDITOR_TYPES


class Attachment:

    def __init__(self, item: dict):
        data = item['data']
        self.key = data.get('key', 'unknown')
        self.parent = data.get('parent', None)  # type: Optional[str]
        if 'parentItem' in data.keys():
            self.parent = data.get('parentItem', None)  # type: Optional[str]
        self.file_hash = data.get('md5', None)  # type: Optional[str]
        self.content_type = data.get('contentType', 'application/octet-stream')  # type: Optional[str]
        self.filename = data.get('filename', self.key)  # type: Optional[str]
        self.title = data.get('title', None)  # type: Optional[str]
        self.mtime = data.get('mtime', None)  # type: Optional[int]
        self.created_at = from_timestamp(data.get('dateAdded', None))  # type: datetime.datetime
        self.updated_at = from_timestamp(data.get('dateModified', None))  # type: datetime.datetime
        self.tags = [tag['tag'] for tag in data.get('tags', [])]  # type: List[str]

    @staticmethod
    def from_items(items: list):
        result = []
        for item in items:
            data = item.get('data', dict())
            item_type = data.get('itemType', '')
            if item_type == 'attachment':
                result.append(Attachment(item))
        return result

    def serialize(self):
        return {
            'key': self.key,
            'parent': self.parent,
            'file_hash': self.file_hash,
            'mtime': self.mtime,
            'title': self.title,
            'filename': self.filename,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'content_type': self.content_type,
            'tags': self.tags,
        }


class LibraryItem:

    def __init__(self, item: dict):
        data = self.data = item['data']
        self.key = data.get('key', 'unknown')  # type: str
        self.title = data.get('title', '(no title given)')  # type: str
        self.type = data.get('itemType', 'unknown')  # type: str
        self.date = data.get('date', None)  # type: Optional[str]
        self.year = None
        if self.date is not None:
            self.year = extract_year(self.date)
        self.doi = data.get('DOI', None)  # type: Optional[str]
        self.isbn = data.get('ISBN', None)  # type: Optional[str]
        self.issn = data.get('ISSN', None)  # type: Optional[str]
        self.publisher = data.get('publisher', None)  # type: Optional[str]
        self.pages = data.get('pages', None)  # type: Optional[str]
        self.conference_name = data.get('conferenceName', None)  # type: Optional[str]
        self.proceedings_title = data.get('proceedingsTitle', None)  # type: Optional[str]
        self.publication_title = data.get('publicationTitle', None)  # type: Optional[str]
        self.journal_abbreviation = data.get('journalAbbreviation', None)  # type: Optional[str]
        self.url = data.get('url', None)  # type: Optional[str]
        self.volume = data.get('volume', None)  # type: Optional[str]
        self.series = data.get('series', None)  # type: Optional[str]
        self.issue = data.get('issue', None)  # type: Optional[str]
        self.created_at = from_timestamp(data.get('dateAdded', None))  # type: datetime.datetime
        self.updated_at = from_timestamp(data.get('dateModified', None))  # type: datetime.datetime

        self.authors = [Author(x) for x in data.get('creators', [])]  # type: List[Author]
        self.attachments = Attachment.from_items(item.get('children', []))  # type: List[Attachment]
        self.tags = [tag['tag'] for tag in data.get('tags', [])]  # type: List[str]


class Collection:

    def __init__(self, items: List[LibraryItem], config: ZoteroxyConfig):
        self.items = items
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        if len(items) > 0:
            self.created_at = min(map(lambda x: x.created_at, self.items))
            self.updated_at = max(map(lambda x: x.updated_at, self.items))
        self.identifier = config.library.id
        self.name = config.library.name
        self.owner = config.library.owner
        self.description = config.library.description
        self.base_url = config.settings.base_url

