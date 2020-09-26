import aiohttp_jinja2
import jinja2
import os

from aiohttp import web

from zoteroxy.config import ZoteroxyConfigParser, ZoteroxyConfig
from zoteroxy.zotero import Zotero


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
        return web.json_response(items)
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


ENV_CONFIG = 'ZOTEROXY_CONFIG'


def init_func(argv):
    app = web.Application()

    # load config
    config_file = os.getenv(ENV_CONFIG)
    cfg = ZoteroxyConfigParser()
    if config_file is not None:
        with open(config_file) as f:
            app['cfg'] = cfg.parse_file(f)
        print(app['cfg'])
    else:
        print('Missing configuration file!')
    app['zotero'] = Zotero(app['cfg'])
    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('zoteroxy', 'templates'))
    app.router.add_get('/', index_handler)
    app.router.add_get('/items', items_handler)
    app.router.add_get('/settings', settings_handler)

    return app
