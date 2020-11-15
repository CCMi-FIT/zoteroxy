import aiohttp_jinja2

from aiohttp import web

from zoteroxy.consts import VERSION
from zoteroxy.serializers import BibJSONSerializer, BibTexSerializer, ZoteroxySerializer
from zoteroxy.zotero import Zotero


class ZoteroxyAPI:

    def __init__(self, zotero: Zotero):
        self.zotero = zotero

    @property
    def config(self):
        return self.zotero.config

    async def view_index(self, request) -> web.Response:
        return aiohttp_jinja2.render_template(
            'index.html.j2', request, {
                'current': 'home',
                'zotero': self.zotero,
                'config': self.config,
            }
        )

    async def view_collection(self, request) -> web.Response:
        return aiohttp_jinja2.render_template(
            'collection.html.j2', request, {
                'current': 'collection',
                'config': self.config,
            }
        )

    async def view_settings(self, request) -> web.Response:
        return aiohttp_jinja2.render_template(
            'settings.html.j2', request, {
                'current': 'settings',
                'config': self.config,
            }
        )

    async def retrieve_file(self, request: web.Request) -> web.Response:
        key = request.match_info.get('key', None)
        if key is None:
            raise web.HTTPBadRequest()
        try:
            metadata = self.zotero.attachment_metadata(key=key)
        except RuntimeError:
            raise web.HTTPNotFound()
        data = self.zotero.attachment_data(metadata=metadata)
        return web.Response(
            body=data,
            content_type=metadata.content_type,
            headers={
                'Content-Disposition': f'inline; filename="{metadata.filename}"'
            }
        )

    async def get_info_json(self) -> web.Response:
        return web.json_response({
            'type': self.config.library.type,
            'id': self.config.library.id,
            'name': self.config.library.name,
            'owner': self.config.library.owner,
            'description': self.config.library.description,
            'zoteroxy': {
                'base_url': self.config.settings.base_url,
                'version': VERSION
            }
        })

    async def get_settings_json(self) -> web.Response:
        return web.json_response({
            'base_url': self.config.settings.base_url,
            'tags': self.config.settings.tags,
            'cache': {
                'duration': self.config.settings.cache_duration,
                'file_duration': self.config.settings.cache_file_duration,
            }
        })

    async def get_collection(self) -> web.Response:
        return web.json_response(
            ZoteroxySerializer.serialize_collection(self.zotero.collection)
        )

    async def get_collection_bib(self) -> web.Response:
        return web.json_response(
            BibTexSerializer.serialize_collection(self.zotero.collection)
        )

    async def get_collection_json(self) -> web.Response:
        return web.json_response(
            BibJSONSerializer.serialize_collection(self.zotero.collection)
        )

    async def purge_cache(self) -> web.Response:
        self.zotero.clear_cache()
        return web.Response(status=204)
