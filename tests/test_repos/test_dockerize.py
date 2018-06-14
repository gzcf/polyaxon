# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import uuid
from pathlib import Path
from unittest.mock import MagicMock

from django.conf import settings
from django.test import override_settings

from dockerizer.builders.experiments import ExperimentDockerBuilder
from dockerizer.builders.utils import login_external_registries
from tests.utils import BaseTest


class TestRepoDockerize(BaseTest):
    def test_get_requirements_and_setup_path_works_as_expected(self):
        # Create a repo folder
        repo_path = os.path.join(settings.REPOS_ROOT, 'repo')
        os.mkdir(repo_path)

        builder = ExperimentDockerBuilder(experiment_name='name',
                                          experiment_uuid=uuid.uuid4().hex,
                                          repo_path=repo_path,
                                          from_image='busybox',
                                          image_name='busycube/busycube',
                                          image_tag='1')
        assert builder.polyaxon_requirements_path is None
        assert builder.polyaxon_setup_path is None
        builder.clean()

        # Add a polyaxon_requirements.txt and polyaxon_setup.sh files to repo path
        Path(os.path.join(repo_path, 'polyaxon_requirements.txt')).touch()
        Path(os.path.join(repo_path, 'polyaxon_setup.sh')).touch()

        builder = ExperimentDockerBuilder(experiment_name='name',
                                          experiment_uuid=uuid.uuid4().hex,
                                          repo_path=repo_path,
                                          from_image='busybox',
                                          image_name='busycube/busycube',
                                          image_tag='1')
        assert builder.polyaxon_requirements_path == 'repo/polyaxon_requirements.txt'
        assert builder.polyaxon_setup_path == 'repo/polyaxon_setup.sh'
        builder.clean()

    def test_render_works_as_expected(self):
        # Create a repo folder
        repo_path = os.path.join(settings.REPOS_ROOT, 'repo')
        os.mkdir(repo_path)

        # By default it should user FROM image declare WORKDIR and COPY code
        builder = ExperimentDockerBuilder(experiment_name='name',
                                          experiment_uuid=uuid.uuid4().hex,
                                          repo_path=repo_path,
                                          from_image='busybox',
                                          image_name='busycube/tets',
                                          image_tag='1.0.0')

        dockerfile = builder.render()
        builder.clean()

        assert 'FROM busybox' in dockerfile
        assert 'WORKDIR {}'.format(builder.WORKDIR) in dockerfile
        assert 'COPY {}'.format(builder.folder_name) in dockerfile

        # Add env vars
        builder = ExperimentDockerBuilder(experiment_name='name',
                                          experiment_uuid=uuid.uuid4().hex,
                                          repo_path=repo_path,
                                          from_image='busybox',
                                          image_name='busycube/tets',
                                          image_tag='0.1.1',
                                          env_vars=[('BLA', 'BLA')])

        dockerfile = builder.render()
        assert 'ENV BLA BLA' in dockerfile
        builder.clean()

        # Add a polyaxon_requirements.txt and polyaxon_setup.sh files to repo path
        Path(os.path.join(repo_path, 'polyaxon_requirements.txt')).touch()
        Path(os.path.join(repo_path, 'polyaxon_setup.sh')).touch()
        # Add step to act on them
        steps = [
            'pip install -r polyaxon_requirements.txt',
            './polyaxon_setup.sh'
        ]

        builder = ExperimentDockerBuilder(experiment_name='name',
                                          experiment_uuid=uuid.uuid4().hex,
                                          repo_path=repo_path,
                                          from_image='busybox',
                                          image_name='busycube/tets',
                                          image_tag='alpha.1',
                                          steps=steps)

        dockerfile = builder.render()
        assert 'COPY {} {}'.format(
            builder.polyaxon_requirements_path, builder.WORKDIR) in dockerfile
        assert 'COPY {} {}'.format(
            builder.polyaxon_setup_path, builder.WORKDIR) in dockerfile

        assert 'RUN {}'.format(steps[0]) in dockerfile
        assert 'RUN {}'.format(steps[1]) in dockerfile
        builder.clean()

    def test_login_external_registries(self):
        with override_settings(
            EXTERNAL_REGISTRIES = [{'host': 'reg.com', 'username': 'user', 'password': '123456'}]
        ):
            docker_builder = MagicMock()
            login_external_registries(docker_builder)
            docker_builder.login.assert_called_once_with(registry_user='user',
                                                         registry_password='123456',
                                                         registry_host='reg.com')

        with override_settings(EXTERNAL_REGISTRIES=None):
            docker_builder = MagicMock()
            login_external_registries(docker_builder)
            docker_builder.login.assert_not_called()

        with override_settings(EXTERNAL_REGISTRIES=''):
            docker_builder = MagicMock()
            login_external_registries(docker_builder)
            docker_builder.login.assert_not_called()
