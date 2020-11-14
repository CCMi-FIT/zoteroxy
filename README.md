# zoteroxy

Proxy service providing data from Zotero in a convenient way

## Installation

Zoteroxy is a [standard Python package](https://packaging.python.org/tutorials/installing-packages/) which you can install:

```
$ git clone https://github.com/CCMi-FIT/zoteroxy.git
$ pip install -e .
```

We recommend to use [virtual environment for Python](https://docs.python.org/3/library/venv.html):

```
$ git clone https://github.com/CCMi-FIT/zoteroxy.git
$ python3.6 -m venv env
$ . env/bin/activate
(env) $ pip install -e .
```

Also, you can build the [Docker](https://www.docker.com) image:

```
$ git clone https://github.com/CCMi-FIT/zoteroxy.git
$ docker build . -t zoteroxy:local
$ docker run zoteroxy:local
```

Or use public one from [Docker Hub](https://hub.docker.com/r/ccmi/zoteroxy):

```
$ docker run ccmi/zoteroxy
```

## Configuration

Configuration is done simply by a single configuration file. You can see
the [example configuration](config.example.yml). First, you will need the 
API key for Zotero, see [their documentation](https://www.zotero.org/support/dev/web_api/v3/basics)
for details. Then, there is configuration of library (`id` and `type` of Zotero
library) together with additional metadata: `name`, `owner`, `description`.

Finally, there are settings affecting how the proxy works. `base_url` serves
for providing in-app links. Then for `tags` you can specify list of tags that
will be used for filtering the items from your library (matching will be published).
How tags can be joined, you can see again in [Zotero docs](https://www.zotero.org/support/dev/web_api/v3/basics#search_parameters_tags-within-items_endpoints).
Optionally, you can configure caching of the proxy in terms of duration and 
directory for caching files (i.e. attachments of library items).

This configuration file needs to be provided to Zoteroxy by giving path in
environment variable `ZOTEROXY_CONFIG`.

## Usage

After running your Zoteroxy instance, visit the index page for further information.
You can also access Swagger API documentation directly in the application.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE)
file for more details
