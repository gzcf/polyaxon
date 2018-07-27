# -*- coding: utf-8 -*-
from django.test import override_settings

from spawners.base import get_pod_volumes
from spawners.templates import constants
from tests.utils import BaseTest


class TestBase(BaseTest):
    def test_get_pod_volumes(self):
        with override_settings(
                DATA_ROOT='/data',
                DATA_CLAIM_NAME='data',
                OUTPUTS_CLAIM_NAME='outputs',
                OUTPUTS_ROOT='/outputs',
                EXTRA_PERSISTENCES=None):
            volumes, volume_mounts = get_pod_volumes()
            assert {v.name for v in volumes} == {constants.DATA_VOLUME,
                                                 constants.OUTPUTS_VOLUME,
                                                 constants.SHM_VOLUME}

    def test_get_pod_volumes_extra(self):
        EXTRA_PERSISTENCES = [{
            'mountPath': '/storage/1',
            'hostPath': '/path/to/storage',
            'readOnly': True
        }, {
            'mountPath': '/storage/2',
            'existingClaim': 'torage-2-pvc'
        }]
        with override_settings(
                DATA_ROOT='/data',
                DATA_CLAIM_NAME='data',
                OUTPUTS_CLAIM_NAME='outputs',
                OUTPUTS_ROOT='/outputs',
                EXTRA_PERSISTENCES=EXTRA_PERSISTENCES):
            volumes, volume_mounts = get_pod_volumes()
            assert len(volumes) == 5
            assert len(volume_mounts) == 5
