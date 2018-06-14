# -*- coding: utf-8 -*-
"""
使用 LDAP 验证代理服务接入零氪内部的域账号体系
"""
from polyaxon.utils import config
from .auth import AUTHENTICATION_BACKENDS

POLYAXON_AUTH_LINKDOC = config.get_boolean('POLYAXON_AUTH_LINKDOC', is_optional=True)

if POLYAXON_AUTH_LINKDOC:
    LDAP_AUTH_PROXY_ENDPOINT = config.get_string('POLYAXON_AUTH_LINKDOC_PROXY').rstrip('/')
    AUTHENTICATION_BACKENDS = ['auth_linkdoc.backend.LinkdocDomainBackend'] + AUTHENTICATION_BACKENDS
