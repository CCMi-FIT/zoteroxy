import aiohttp_jinja2
import aiohttp_cors
import aiohttp_swagger
import functools
import humps
import jinja2
import os
import pathlib

from aiohttp import web

from zoteroxy.api import ZoteroxyAPI
from zoteroxy.config import ZoteroxyConfigParser
from zoteroxy.consts import APPNAME, DESCRIPTION, VERSION, ENV_CONFIG
from zoteroxy.zotero import Zotero


filters = dict()
routes = list()


def zoteroxy_jinja_filter(name: str):
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        filters[name] = wrapped
        return wrapped
    return wrapper


def zoteroxy_endpoint(method: str, route: str, *, name: str, cors: bool = True):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(request):
            api = request.app['api']
            return await func(request=request, api=api)
        routes.append(
            (method, route, wrapped, name, cors)
        )
        return wrapped
    return wrapper


@zoteroxy_jinja_filter('decamelize')
def decamelize_filter(text):
    return humps.decamelize(text).replace('_', ' ').capitalize()


@zoteroxy_endpoint('GET', '/', name='index')
async def index_handler(request, api: ZoteroxyAPI):
    """
    ---
    description: Basic information about the proxy instance.
    produces:
    - application/json
    - text/html
    responses:
        "200":
            description: proxy information
    """
    if request.headers['Accept'] == 'application/json':
        return await api.get_info_json()
    else:
        return await api.view_index(request)


@zoteroxy_endpoint('GET', '/collection', name='collection')
async def items_handler(request, api: ZoteroxyAPI):
    """
    ---
    description: Serialized collection of library items.
    produces:
    - application/json
    - application/x-bibtex
    - text/html
    responses:
        "200":
            description: library items
    """
    if request.headers['Accept'] == 'application/json':
        return await api.get_collection()
    elif request.headers['Accept'] == 'application/x-bibtex':
        return await api.get_collection_bib()
    else:
        return await api.view_collection(request)


@zoteroxy_endpoint('GET', '/collection.json', name='collection_json')
async def items_json_handler(request, api: ZoteroxyAPI):
    """
    ---
    description: Library items in BibJSON format.
    produces:
    - application/json
    responses:
        "200":
            description: library items
    """
    return await api.get_collection_json()


@zoteroxy_endpoint('GET', '/collection.bib', name='collection_bib')
async def items_bib_handler(request, api: ZoteroxyAPI):
    """
    ---
    description: Library items in BibTeX format.
    produces:
    - application/x-bibtex
    responses:
        "200":
            description: library items
    """
    return await api.get_collection_bib()


@zoteroxy_endpoint('GET', '/settings', name='settings')
async def settings_handler(request, api: ZoteroxyAPI):
    """
    ---
    description: Settings information about the proxy instance.
    produces:
    - application/json
    - text/html
    responses:
        "200":
            description: settings information
    """
    if request.headers['Accept'] == 'application/json':
        return await api.get_settings_json()
    else:
        return await api.view_settings(request)


@zoteroxy_endpoint('GET', '/file/{key}', name='file', cors=False)
async def file_retrieve_handler(request, api: ZoteroxyAPI):
    """
    ---
    description: Retrieve file content based on given key
    responses:
        "200":
            description: file content
        "400":
            description: invalid key
        "404":
            description: file with given key is not available
    """
    return await api.retrieve_file(request)


@zoteroxy_endpoint('POST', '/purge', name='purge_cache', cors=False)
async def purge_cache_handler(request, api: ZoteroxyAPI):
    """
    ---
    description: Purge caches of the proxy.
    produces:
    - application/x-bibtex
    responses:
        "204":
            description: cache has been purged
    """
    return await api.purge_cache()


def init_func(argv):
    app = web.Application()
    app_root = pathlib.Path(__file__).parent.absolute()

    # load config
    config_file = os.getenv(ENV_CONFIG)
    cfg = ZoteroxyConfigParser()
    if config_file is not None:
        with open(config_file) as f:
            app['cfg'] = cfg.parse_file(f)
    else:
        print('Missing configuration file!')
    app['api'] = ZoteroxyAPI(Zotero(app['cfg']))

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
    })

    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('zoteroxy', 'templates'),
        filters=filters,
    )
    app.router.add_static('/static/', path=app_root / 'static', name='static')
    app['static_root_url'] = '/static'

    for method, path, handler, name, use_cors in routes:
        route = app.router.add_route(method=method, path=path, handler=handler, name=name)
        if use_cors:
            cors.add(route)

    aiohttp_swagger.setup_swagger(
        app=app,
        swagger_url='/swagger-ui',
        title=APPNAME,
        description=DESCRIPTION,
        api_version=VERSION
    )

    return app
