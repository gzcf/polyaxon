# -*- coding: utf-8 -*-
from django.conf import settings


def login_external_registries(docker_builder):
    registries = settings.EXTERNAL_REGISTRIES
    if not registries:
        return

    for reg in registries:
        docker_builder.login(registry_user=reg['username'],
                             registry_password=reg['password'],
                             registry_host=reg['host'])
