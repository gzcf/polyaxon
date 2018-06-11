# -*- coding: utf-8 -*-
"""
使用 LDAP 验证代理服务接入零氪内部的域账号体系
"""
from .auth import AUTHENTICATION_BACKENDS

POLYAXON_AUTH_LINKDOC = True

if POLYAXON_AUTH_LINKDOC:
    LDAP_AUTH_PROXY_ENDPOINT = 'http://172.16.0.128:8080'
    AUTHENTICATION_BACKENDS = ['auth_linkdoc.backend.LinkdocDomainBackend'] + AUTHENTICATION_BACKENDS
