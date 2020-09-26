#!/bin/bash

export ZOTEROXY_CONFIG=config.yml
python -m aiohttp.web zoteroxy:init_func
