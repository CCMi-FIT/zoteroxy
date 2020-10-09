import aiohttp_jinja2
import aiohttp_cors
import humps
import jinja2
import os
import pathlib

from aiohttp import web

from zoteroxy.config import ZoteroxyConfigParser, ZoteroxyConfig
from zoteroxy.zotero import Zotero


def decamelize_filter(text):
    return humps.decamelize(text).replace('_', ' ').capitalize()


async def index_handler(request):
    config = request.app['cfg']
    zotero = request.app['zotero']
    if request.headers['Accept'] == 'application/json':
        return web.json_response(zotero.library.key_info())
    else:
        return aiohttp_jinja2.render_template(
            'index.html.j2', request, {
                'current': 'home',
                'zotero': zotero,
                'config': config,
            }
        )


async def items_handler(request):
    zotero = request.app['zotero']
    items = zotero.items()
    if request.headers['Accept'] == 'application/json':
        return web.json_response([item.serialize() for item in items])
    else:
        return aiohttp_jinja2.render_template(
            'items.html.j2', request, {
                'current': 'items',
                'items': items,
            }
        )


async def settings_handler(request):
    config = request.app['cfg']  # type: ZoteroxyConfig
    if request.headers['Accept'] == 'application/json':
        return web.json_response({
            'tags': config.settings.tags,
            'cache': {
                'duration': config.settings.cache_duration
            }
        })
    else:
        return aiohttp_jinja2.render_template(
            'settings.html.j2', request, {
                'current': 'settings',
                'config': config,
            }
        )


async def file_retrieve_handler(request):
    key = request.match_info.get('key', None)
    if key is None:
        raise web.HTTPBadRequest()
    zotero = request.app['zotero']  # type: Zotero
    try:
        metadata = zotero.attachment_metadata(key=key)
    except RuntimeError:
        raise web.HTTPNotFound()
    data = zotero.attachment_data(metadata=metadata)
    return web.Response(
        body=data,
        content_type=metadata.content_type,
        headers={
            'Content-Disposition': f'inline; filename="{metadata.filename}"'
        }
    )


ENV_CONFIG = 'ZOTEROXY_CONFIG'


def init_func(argv):
    app = web.Application()
    PROJECT_ROOT = pathlib.Path(__file__).parent.absolute()

    # load config
    config_file = os.getenv(ENV_CONFIG)
    cfg = ZoteroxyConfigParser()
    if config_file is not None:
        with open(config_file) as f:
            app['cfg'] = cfg.parse_file(f)
    else:
        print('Missing configuration file!')
    app['zotero'] = Zotero(app['cfg'])

    cors_enabled_routes = []

    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('zoteroxy', 'templates'),
        filters={'decamelize': decamelize_filter},
    )
    app.router.add_static('/static/',
                          path=PROJECT_ROOT / 'static',
                          name='static')
    app['static_root_url'] = '/static'
    cors_enabled_routes.append(app.router.add_get('/', index_handler, name='index'))
    cors_enabled_routes.append(app.router.add_get('/items', items_handler, name='items'))
    cors_enabled_routes.append(app.router.add_get('/settings', settings_handler, name='settings'))
    app.router.add_get('/file/{key}', file_retrieve_handler, name='file')

    cors = aiohttp_cors.setup(app)
    for route in cors_enabled_routes:
        cors.add(route, {
            "*": aiohttp_cors.ResourceOptions(expose_headers="*", allow_headers="*"),
        })

    return app
