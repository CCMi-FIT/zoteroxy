#!/bin/bash

export ZOTEROXY_CONFIG=config.yml
python -m aiohttp.web -H 0.0.0.0 -P 8888 zoteroxy:init_func
