from typing import Optional

from zoteroxy.model import Collection, LibraryItem


class BaseSerializer:

    def serialize_item(self, item: LibraryItem) -> dict:
        raise NotImplementedError()

    def serialize_collection(self, collection: Collection) -> dict:
        raise NotImplementedError()


class BibTexSerializer(BaseSerializer):

    _TYPES = {
        'artwork': 'misc',
        'audioRecording': 'misc',
        'bill': 'misc',
        'blogPost': 'misc',
        'book': 'book',
        'bookSection': 'inbook',
        'case': 'misc',
        'conferencePaper': 'inproceedings',
        'dictionaryEntry': 'misc',
        'document': 'misc',
        'email': 'misc',
        'encyclopediaArticle': 'article',
        'film': 'film',
        'forumPost': 'misc',
        'hearing': 'misc',
        'instantMessage': 'misc',
        'interview': 'misc',
        'journalArticle': 'article',
        'letter': 'misc',
        'magazineArticle': 'article',
        'manuscript': 'misc',
        'map': 'misc',
        'newspaperArticle': 'article',
        'patent': 'misc',
        'podcast': 'misc',
        'presentation': 'misc',
        'radioBroadcast': 'misc',
        'report': 'techreport',
        'software': 'misc',
        'statute': 'misc',
        'thesis': 'phdthesis',
        'tvBroadcast': 'misc',
        'videoRecording': 'misc',
        'webpage': 'misc',
    }

    _DEFAULT_TYPE = 'misc'

    _ATTRIBUTES = {
        'title': ['title'],
        'doi': ['doi'],
        'pages': ['pages'],
        'publisher': ['publisher'],
        'journal': ['proceedings_title', 'publication_title', 'journal_abbreviation'],
        'series': ['series'],
        'volume': ['volume'],
        'year': ['year'],
        'url': ['url'],
        'number': ['issue'],
        'isbn': ['isbn'],
        'issn': ['issn'],
    }

    @classmethod
    def build_pairs(cls, item: LibraryItem) -> dict:
        pairs = {}
        for key, attrs in cls._ATTRIBUTES.items():
            for attr in attrs:
                v = getattr(item, attr, None)
                if v is not None and v != '':
                    pairs[key] = v
                    break
        authors = []
        editors = []
        for author in item.authors:
            if author.is_author:
                authors.append(f'{author.lastname}, {author.firstname}')
            elif author.is_editor:
                editors.append(f'{author.lastname}, {author.firstname}')
        if len(authors) > 0:
            pairs['author'] = ' and '.join(authors)
        if len(editors) > 0:
            pairs['editor'] = ' and '.join(editors)
        return pairs

    @classmethod
    def guess_bib_type(cls, item: LibraryItem) -> str:
        return cls._TYPES.get(item.type, cls._DEFAULT_TYPE)

    @classmethod
    def create_bib_str(cls, item: LibraryItem) -> str:
        pairs = cls.build_pairs(item)
        bibtype = cls.guess_bib_type(item)
        key = item.key
        lines = '\n'.join((f'{key} = "{value}"' for key, value in pairs.items()))
        return f'@{bibtype}{{{key},\n{lines}\n}}'

    @classmethod
    def serialize_item(cls, item: LibraryItem) -> dict:
        return {'bib': cls.create_bib_str(item)}

    @classmethod
    def serialize_collection(cls, collection: Collection) -> dict:
        bibs = [cls.serialize_item(item)['bib'] for item in collection.items]
        collection = ',\n'.join(bibs)
        return {
            'total_items': len(bibs),
            'bib': collection
        }


class BibJSONSerializer(BaseSerializer):

    CUSTOM_FIELDS = frozenset([
        'author',
        'editor',
        'link',
    ])

    @classmethod
    def serialize_item(cls, item: LibraryItem, collection: Optional[str] = None) -> dict:
        record = {
            'type': BibTexSerializer.guess_bib_type(item),
            'id': item.key,
            '_bib': BibTexSerializer.create_bib_str(item),
        }
        for k, v in BibTexSerializer.build_pairs(item).items():
            if k not in cls.CUSTOM_FIELDS:
                record[k] = v
        record['author'] = []
        record['editor'] = []
        for author in item.authors:
            person = {
                'name': f'{author.lastname}, {author.firstname}',
                'firstname': author.firstname,
                'lastname': author.lastname,
            }
            if author.is_author:
                record['author'].append(person)
            elif author.is_editor:
                record['editor'].append(person)
        if 'journal' in record.keys():
            identifiers = []
            if item.issn is not None:
                identifiers.append({
                    'type': 'issn',
                    'id': item.issn
                })
            if item.isbn is not None:
                identifiers.append({
                    'type': 'isbn',
                    'id': item.isbn
                })
            record['journal'] = {
                'name': record['journal'],
                'identifier': identifiers,
            }
            if item.pages is not None:
                record['journal']['pages'] = item.pages
            if item.volume is not None:
                record['journal']['volume'] = item.volume
            if item.issue is not None:
                record['journal']['issue'] = item.issue
        if collection is not None:
            record['collection'] = collection
        # TODO: link for multiple attachments
        return {k: v for k, v in record.items() if v is not None}

    @classmethod
    def serialize_collection(cls, collection: Collection) -> dict:
        records = [cls.serialize_item(item, collection=collection.identifier)
                   for item in collection.items]
        return {
            'metadata': {
                'collection': collection.identifier,
                'label': collection.name,
                'description': collection.description,
                'owner': collection.owner,
                'created': collection.created_at.isoformat(),
                'modified': collection.updated_at.isoformat(),
                'source': f'{collection.base_url}/collection.bib',
                'records': len(records),
            },
            'records': records
        }


class ZoteroxySerializer(BaseSerializer):

    @classmethod
    def serialize_item(cls, item: LibraryItem) -> dict:
        return {
            # 'data': item.data,
            'key': item.key,
            'title': item.title,
            'type': item.type,
            'date': item.date,
            'year': item.year,
            'doi': item.doi,
            'isbn': item.isbn,
            'issn': item.issn,
            'publisher': item.publisher,
            'pages': item.pages,
            'conferenceName': item.conference_name,
            'proceedingsTitle': item.proceedings_title,
            'publicationTitle': item.publication_title,
            'journalAbbreviation': item.journal_abbreviation,
            'url': item.url,
            'volume': item.volume,
            'series': item.series,
            'issue': item.issue,
            'authors': [a.serialize() for a in item.authors],
            'attachments': [a.serialize() for a in item.attachments],
            'tags': item.tags,
            'bibtex': BibTexSerializer.create_bib_str(item),
            'bibjson': BibJSONSerializer.serialize_item(item)
        }

    @classmethod
    def serialize_collection(cls, collection: Collection) -> dict:
        return {
            'total_items': len(collection.items),
            'items': [cls.serialize_item(item) for item in collection.items]
        }
