# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import json

from polyaxon.utils import config

REGISTRY_USER = config.get_string('POLYAXON_REGISTRY_USER', is_optional=True)
REGISTRY_PASSWORD = config.get_string('POLYAXON_REGISTRY_PASSWORD', is_optional=True)
REGISTRY_HOST_NAME = config.get_string('POLYAXON_REGISTRY_HOST', is_optional=True)
REGISTRY_PORT = config.get_string('POLYAXON_REGISTRY_PORT', is_optional=True)
REGISTRY_NODE_PORT = config.get_string('POLYAXON_REGISTRY_NODE_PORT', is_optional=True)
REGISTRY_HOST = '{}:{}'.format('127.0.0.1', REGISTRY_NODE_PORT)

EXTERNAL_REGISTRIES = config.get_string('POLYAXON_EXTERNAL_REGISTRIES', is_optional=True)
if EXTERNAL_REGISTRIES:
    # [{'host': 'registry.company.com', 'username': 'user', 'password': '123456'}]
    EXTERNAL_REGISTRIES = json.loads(EXTERNAL_REGISTRIES)