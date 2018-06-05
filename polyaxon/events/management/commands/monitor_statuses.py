# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import time

from django.conf import settings
from django.db import InterfaceError, connection
from kubernetes.client.rest import ApiException
from polyaxon_k8s.manager import K8SManager

from events.management.commands._base_monitor import BaseMonitorCommand
from events.monitors import statuses


class Command(BaseMonitorCommand):
    help = 'Watch jobs statuses events.'

    def handle(self, *args, **options):
        log_sleep_interval = options['log_sleep_interval']
        self.stdout.write(
            "Started a new statuses monitor with, "
            "log sleep interval: `{}`.".format(log_sleep_interval),
            ending='\n')
        k8s_manager = K8SManager(namespace=settings.K8S_NAMESPACE, in_cluster=True)
        while True:
            try:
                statuses.run(k8s_manager)
            except ApiException as e:
                statuses.logger.error(
                    "Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
                time.sleep(log_sleep_interval)
            except InterfaceError:
                # In some cases such as timeout, database restart, connection will be closed by remote peer.
                # Django cannot recover from this condition automatically.
                # Here we close dead connection manually, make Django to reconnect next time querying DB.
                connection.close()
                statuses.logger.warn(
                    "Database connection is already closed by peer, discard old connection\n")
            except Exception as e:
                statuses.logger.exception("Unhandled exception occurred %s\n" % e)
