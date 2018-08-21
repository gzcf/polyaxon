# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import mock

from unittest.mock import patch

from rest_framework import status

from factories.factory_plugins import TensorboardJobFactory, NotebookJobFactory
from factories.factory_repos import RepoFactory
from factories.fixtures import plugin_spec_parsed_content
from libs.views import ProtectedView
from plugins.models import TensorboardJob, NotebookJob
from plugins.serializers import TensorboardJobSerializer, NotebookJobSerializer
from polyaxon.urls import API_V1
from projects.models import Project
from factories.factory_projects import ProjectFactory
from schedulers import notebook_scheduler
from spawners.project_spawner import ProjectSpawner
from spawners.tensorboard_spawner import TensorboardSpawner
from spawners.notebook_spawner import NotebookSpawner
from spawners.templates.constants import DEPLOYMENT_NAME
from spawners.utils.constants import JobLifeCycle
from tests.utils import BaseViewTest, BaseTransactionViewTest



class BaseTestPluginJobListViewV1(BaseTransactionViewTest):
    serializer_class = None

    def get_url(self):
        raise NotImplementedError

    def get_objects(self):
        raise NotImplementedError

    def get_queryset(self):
        raise NotImplementedError

    def test_get(self):
        resp = self.auth_client.get(self.get_url())
        assert resp.status_code == status.HTTP_200_OK

        assert resp.data['next'] is None
        assert resp.data['count'] == len(self.get_objects())

        data = resp.data['results']
        assert len(data) == self.get_queryset().count()
        assert data == self.serializer_class(self.get_queryset(), many=True).data

    def test_get_running_experiments(self):
        url = self.get_url() + '?is_running=1'
        resp = self.auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

        assert resp.data['next'] is None

        running_count = len(self.get_queryset().filter(job_status__status__in=JobLifeCycle.RUNNING_STATUS))
        assert resp.data['count'] == running_count

        data = resp.data['results']
        for job in data:
            assert job['last_status'] in JobLifeCycle.RUNNING_STATUS

    def test_get_order_by_created_at_desc(self):
        url = self.get_url() + '?ordering=-created_at'
        resp = self.auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data['results']
        prev_created_at = None
        for job in data:
            assert prev_created_at is None or prev_created_at >= job['created_at']
            prev_created_at = job['created_at']

        url = self.get_url() + '?ordering=-created_at&is_running=1'
        resp = self.auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

        data = resp.data['results']
        prev_created_at = None
        for job in data:
            assert job['last_status'] in JobLifeCycle.RUNNING_STATUS
            assert prev_created_at is None or prev_created_at >= job['created_at']
            prev_created_at = job['created_at']


    def test_ordering_with_pagination(self):
        limit = len(self.get_objects()) - 1
        url = self.get_url() + '?ordering=-created_at&limit={}'.format(limit)
        resp = self.auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

        next = resp.data.get('next')
        assert next is not None
        assert resp.data['count'] == self.get_queryset().count()

        data = resp.data['results']
        assert len(data) == limit
        prev_created_at = None
        for job in data:
            assert prev_created_at is None or prev_created_at >= job['created_at']
            prev_created_at = job['created_at']

        resp = self.auth_client.get(next)
        assert resp.status_code == status.HTTP_200_OK

        assert resp.data['next'] is None

        data = resp.data['results']
        assert len(data) == 1
        assert prev_created_at >= data[0]['created_at']


    def test_pagination(self):
        limit = len(self.get_objects()) - 1
        resp = self.auth_client.get("{}?limit={}".format(self.url, limit))
        assert resp.status_code == status.HTTP_200_OK

        next = resp.data.get('next')
        assert next is not None
        assert resp.data['count'] == self.get_queryset().count()

        data = resp.data['results']
        assert len(data) == limit
        assert data == self.serializer_class(self.get_queryset()[:limit], many=True).data

        resp = self.auth_client.get(next)
        assert resp.status_code == status.HTTP_200_OK

        assert resp.data['next'] is None

        data = resp.data['results']
        assert len(data) == 1
        assert data == self.serializer_class(self.get_queryset()[limit:], many=True).data


class TestTensorboardJobListViewV1(BaseTestPluginJobListViewV1):
    model_class = TensorboardJob
    factory_class = TensorboardJobFactory
    serializer_class = TensorboardJobSerializer
    HAS_AUTH = False

    def get_url(self):
        return self.url

    def get_objects(self):
        return self.objects

    def get_queryset(self):
        return self.queryset

    def setUp(self):
        super().setUp()
        self.objects = []
        statuses = [JobLifeCycle.CREATED, JobLifeCycle.BUILDING,
                    JobLifeCycle.RUNNING, JobLifeCycle.SUCCEEDED]
        for i in range(len(statuses)):
            object = self.factory_class()
            object.set_status(statuses[i])
            project = ProjectFactory()
            project.tensorboard = object
            project.save()
            self.objects.append(object)
        self.url = '/{}/tensorboard_jobs'.format(API_V1)
        self.queryset = self.model_class.objects.all()


class TestNotebookJobListViewV1(BaseTestPluginJobListViewV1):
    model_class = NotebookJob
    factory_class = NotebookJobFactory
    serializer_class = NotebookJobSerializer
    HAS_AUTH = False

    def get_url(self):
        return self.url

    def get_objects(self):
        return self.objects

    def get_queryset(self):
        return self.queryset

    def setUp(self):
        super().setUp()
        self.objects = []
        statuses = [JobLifeCycle.CREATED, JobLifeCycle.BUILDING,
                    JobLifeCycle.RUNNING, JobLifeCycle.SUCCEEDED]
        for _ in range(len(statuses)):
            object = self.factory_class()
            project = ProjectFactory()
            project.notebook = object
            project.save()
            self.objects.append(object)
        self.url = '/{}/notebook_jobs'.format(API_V1)
        self.queryset = self.model_class.objects.all()


del BaseTestPluginJobListViewV1


class TestStartTensorboardViewV1(BaseTransactionViewTest):
    model_class = Project
    factory_class = ProjectFactory
    HAS_AUTH = True

    def setUp(self):
        super().setUp()
        self.object = self.factory_class(user=self.auth_client.user)
        self.url = '/{}/{}/{}/tensorboard/start'.format(
            API_V1,
            self.object.user.username,
            self.object.name)
        self.queryset = self.model_class.objects.all()

    def test_start(self):
        assert self.queryset.count() == 1
        assert self.object.tensorboard is None
        with patch('projects.tasks.start_tensorboard.delay') as mock_fct:
            resp = self.auth_client.post(self.url)
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1
        self.object.refresh_from_db()
        assert isinstance(self.object.tensorboard, TensorboardJob)

    def test_spawner_start(self):
        assert self.queryset.count() == 1
        with patch('schedulers.tensorboard_scheduler.start_tensorboard') as mock_fct:
            resp = self.auth_client.post(self.url)
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1

    def test_start_with_updated_config(self):
        with patch('projects.tasks.start_tensorboard.delay') as mock_fct:
            resp = self.auth_client.post(self.url)
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        # Start with default config
        self.object.refresh_from_db()
        config = self.object.tensorboard.config

        # Simulate stop the tensorboard
        self.object.has_tensorboard = False
        self.object.save()

        # Starting the tensorboard without config should pass
        with patch('projects.tasks.start_tensorboard.delay') as mock_fct:
            resp = self.auth_client.post(self.url)
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        # Check that still using same config
        self.object.tensorboard.refresh_from_db()
        assert config == self.object.tensorboard.config

        # Simulate stop the tensorboard
        self.object.has_tensorboard = False
        self.object.save()

        # Starting again the tensorboard with different config
        with patch('projects.tasks.start_tensorboard.delay') as mock_fct:
            resp = self.auth_client.post(self.url,
                                         data={'config': plugin_spec_parsed_content.parsed_data})

        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        self.object.tensorboard.refresh_from_db()
        # Check that the image was update
        assert config != self.object.tensorboard.config

    def test_start_during_build_process(self):
        with patch('projects.tasks.start_tensorboard.delay') as start_mock:
            self.auth_client.post(self.url)
        self.object.refresh_from_db()
        assert start_mock.call_count == 1
        assert self.object.tensorboard.last_status == JobLifeCycle.CREATED

        # Check that user cannot start a new job if it's already building
        self.object.tensorboard.set_status(status=JobLifeCycle.BUILDING)
        with patch('projects.tasks.start_tensorboard.delay') as start_mock:
            self.auth_client.post(self.url)
        assert start_mock.call_count == 0


class TestStopTensorboardViewV1(BaseViewTest):
    model_class = Project
    factory_class = ProjectFactory
    HAS_AUTH = True

    def setUp(self):
        super().setUp()
        self.object = self.factory_class(user=self.auth_client.user, has_tensorboard=True)
        self.url = '/{}/{}/{}/tensorboard/stop'.format(
            API_V1,
            self.object.user.username,
            self.object.name)
        self.queryset = self.model_class.objects.all()

    def test_stop(self):
        data = {}
        assert self.queryset.count() == 1
        with patch('projects.tasks.stop_tensorboard.delay') as mock_fct:
            resp = self.auth_client.post(self.url, data)
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1

    def test_spawner_stop(self):
        data = {}
        assert self.queryset.count() == 1
        with patch('schedulers.tensorboard_scheduler.stop_tensorboard') as mock_fct:
            resp = self.auth_client.post(self.url, data)
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1


class TestStartNotebookViewV1(BaseTransactionViewTest):
    model_class = Project
    factory_class = ProjectFactory
    HAS_AUTH = True

    def setUp(self):
        super().setUp()
        self.object = self.factory_class(user=self.auth_client.user)
        self.url = '/{}/{}/{}/notebook/start'.format(
            API_V1,
            self.object.user.username,
            self.object.name)
        self.queryset = self.model_class.objects.all()

    def test_post_without_config_fails(self):
        resp = self.auth_client.post(self.url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_build(self):
        data = {'config': plugin_spec_parsed_content.parsed_data}
        assert self.queryset.count() == 1
        assert self.object.notebook is None
        with patch('projects.tasks.build_notebook.delay') as mock_fct:
            resp = self.auth_client.post(self.url, data)
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1
        self.object.refresh_from_db()
        assert isinstance(self.object.notebook, NotebookJob)

    def test_start(self):
        data = {'config': plugin_spec_parsed_content.parsed_data}
        assert self.queryset.count() == 1
        with patch('dockerizer.builders.notebooks.build_notebook_job') as build_mock_fct:
            with patch('projects.tasks.start_notebook.delay') as mock_fct:
                resp = self.auth_client.post(self.url, data)
        assert build_mock_fct.call_count == 1
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1

    def test_build_with_updated_config(self):
        data = {'config': plugin_spec_parsed_content.parsed_data}
        with patch('projects.tasks.build_notebook.delay') as mock_fct:
            resp = self.auth_client.post(self.url, data)

        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        # Start with default config
        self.object.refresh_from_db()
        config = self.object.notebook.config

        # Simulate stop the notebook
        self.object.has_notebook = False
        self.object.save()

        # Starting the notebook without config should pass
        with patch('projects.tasks.build_notebook.delay') as mock_fct:
            resp = self.auth_client.post(self.url)

        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        # Check that still using same config
        self.object.notebook.refresh_from_db()
        assert config == self.object.notebook.config

        # Simulate stop the notebook
        self.object.has_notebook = False
        self.object.save()

        # Starting again the notebook with different config
        data['config']['run']['image'] = 'image_v2'
        with patch('projects.tasks.build_notebook.delay') as _:
            self.auth_client.post(self.url, data)

        self.object.notebook.refresh_from_db()
        # Check that the image was update
        assert config != self.object.notebook.config

    def test_start_during_build_process(self):
        data = {'config': plugin_spec_parsed_content.parsed_data}
        with patch('projects.tasks.build_notebook.delay') as start_mock:
            resp = self.auth_client.post(self.url, data=data)

        assert resp.status_code == status.HTTP_200_OK
        self.object.refresh_from_db()
        assert start_mock.call_count == 1
        assert self.object.notebook.last_status == JobLifeCycle.CREATED

        # Check that user cannot start a new job if it's already building
        self.object.notebook.set_status(status=JobLifeCycle.BUILDING)
        with patch('projects.tasks.build_notebook.delay') as start_mock:
            resp = self.auth_client.post(self.url)

        assert resp.status_code == status.HTTP_200_OK
        assert start_mock.call_count == 0


class TestStopNotebookViewV1(BaseViewTest):
    model_class = Project
    factory_class = ProjectFactory
    HAS_AUTH = True

    def setUp(self):
        super().setUp()
        self.object = self.factory_class(user=self.auth_client.user, has_notebook=True)
        RepoFactory(project=self.object)
        self.url = '/{}/{}/{}/notebook/stop'.format(
            API_V1,
            self.object.user.username,
            self.object.name)
        self.queryset = self.model_class.objects.all()

    def test_stop(self):
        data = {}
        assert self.queryset.count() == 1
        with patch('projects.tasks.stop_notebook.delay') as mock_fct:
            with patch('repos.git.commit') as mock_git_commit:
                with patch('repos.git.undo') as mock_git_undo:
                    resp = self.auth_client.post(self.url, data)
        assert mock_fct.call_count == 1
        assert mock_git_commit.call_count == 1
        assert mock_git_undo.call_count == 0
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1

    def test_stop_without_committing(self):
        data = {'commit': False}
        assert self.queryset.count() == 1
        with patch('projects.tasks.stop_notebook.delay') as mock_fct:
            with patch('repos.git.commit') as mock_git_commit:
                with patch('repos.git.undo') as mock_git_undo:
                    resp = self.auth_client.post(self.url, data)
        assert mock_fct.call_count == 1
        assert mock_git_commit.call_count == 0
        assert mock_git_undo.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1

    def test_spawner_stop(self):
        data = {}
        assert self.queryset.count() == 1
        with patch('schedulers.notebook_scheduler.stop_notebook') as mock_fct:
            resp = self.auth_client.post(self.url, data)
        assert mock_fct.call_count == 1
        assert resp.status_code == status.HTTP_200_OK
        assert self.queryset.count() == 1


class BaseTestPluginViewV1(BaseViewTest):
    plugin_app = ''

    @classmethod
    def _get_url(cls, project, path=None):
        url = '/{}/{}/{}'.format(
            cls.plugin_app,
            project.user.username,
            project.name)

        if path:
            url = '{}/{}'.format(url, path)
        return url

    @classmethod
    def _get_service_url(cls, deployment_name):
        return ProjectSpawner._get_proxy_url(
            namespace='polyaxon',
            job_name=cls.plugin_app,
            deployment_name=deployment_name,
            port=12503)

    def test_rejects_anonymous_user_and_redirected_to_login_page(self):
        project = ProjectFactory()
        response = self.client.get(self._get_url(project))
        assert response.status_code == 302

    def test_rejects_user_with_no_privileges(self):
        project = ProjectFactory(is_public=False)
        response = self.auth_client.get(self._get_url(project))
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_project_with_no_job(self):
        project = ProjectFactory(user=self.auth_client.user)
        response = self.auth_client.get(self._get_url(project))
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTensorboardViewV1(BaseTestPluginViewV1):
    plugin_app = TensorboardSpawner.TENSORBOARD_JOB_NAME

    def test_project_requests_tensorboard_url(self):
        project = ProjectFactory(user=self.auth_client.user, has_tensorboard=True)
        with patch('schedulers.tensorboard_scheduler.get_tensorboard_url') as mock_fct:
            response = self.auth_client.get(self._get_url(project))

        assert mock_fct.call_count == 1
        assert response.status_code == 200

    @mock.patch('schedulers.tensorboard_scheduler.TensorboardSpawner')
    def test_redirects_to_proxy_protected_url(self, spawner_mock):
        project = ProjectFactory(user=self.auth_client.user, has_tensorboard=True)
        deployment_name = DEPLOYMENT_NAME.format(
            project_uuid=project.uuid.hex, name=self.plugin_app)
        service_url = self._get_service_url(deployment_name=deployment_name)
        mock_instance = spawner_mock.return_value
        mock_instance.get_tensorboard_url.return_value = service_url

        response = self.auth_client.get(self._get_url(project))
        assert response.status_code == 200
        self.assertTrue(ProtectedView.NGINX_REDIRECT_HEADER in response)
        proxy_url = '{}/'.format(service_url)
        self.assertEqual(response[ProtectedView.NGINX_REDIRECT_HEADER], proxy_url)

    @mock.patch('schedulers.tensorboard_scheduler.TensorboardSpawner')
    def test_redirects_to_proxy_protected_url_with_extra_path(self, spawner_mock):
        project = ProjectFactory(user=self.auth_client.user, has_tensorboard=True)
        deployment_name = DEPLOYMENT_NAME.format(
            project_uuid=project.uuid.hex, name=self.plugin_app)
        service_url = self._get_service_url(deployment_name=deployment_name)
        mock_instance = spawner_mock.return_value
        mock_instance.get_tensorboard_url.return_value = service_url

        # To `tree?`
        response = self.auth_client.get(self._get_url(project, 'tree?'))
        assert response.status_code == 200
        self.assertTrue(ProtectedView.NGINX_REDIRECT_HEADER in response)
        proxy_url = '{}/{}'.format(
            service_url,
            'tree/'
        )
        self.assertEqual(response[ProtectedView.NGINX_REDIRECT_HEADER], proxy_url)

        # To static files
        response = self.auth_client.get(
            self._get_url(project, 'static/components/something?v=4.7.0'))
        assert response.status_code == 200
        self.assertTrue(ProtectedView.NGINX_REDIRECT_HEADER in response)
        proxy_url = '{}/{}'.format(
            service_url,
            'static/components/something?v=4.7.0'
        )
        self.assertEqual(response[ProtectedView.NGINX_REDIRECT_HEADER], proxy_url)


class TestNotebookViewV1(BaseTestPluginViewV1):
    plugin_app = NotebookSpawner.NOTEBOOK_JOB_NAME

    def test_project_requests_notebook_url(self):
        project = ProjectFactory(user=self.auth_client.user, has_notebook=True)
        with patch('schedulers.notebook_scheduler.get_notebook_url') as mock_url_fct:
            with patch('schedulers.notebook_scheduler.get_notebook_token') as mock_token_fct:
                response = self.auth_client.get(self._get_url(project))

        assert mock_url_fct.call_count == 1
        assert mock_token_fct.call_count == 1
        assert response.status_code == 200

    @mock.patch('schedulers.notebook_scheduler.NotebookSpawner')
    def test_redirects_to_proxy_protected_url(self, spawner_mock):
        project = ProjectFactory(user=self.auth_client.user, has_notebook=True)
        deployment_name = DEPLOYMENT_NAME.format(
            project_uuid=project.uuid.hex, name=self.plugin_app)
        service_url = self._get_service_url(deployment_name=deployment_name)
        mock_instance = spawner_mock.return_value
        mock_instance.get_notebook_url.return_value = service_url

        response = self.auth_client.get(self._get_url(project))
        assert response.status_code == 200
        self.assertTrue(ProtectedView.NGINX_REDIRECT_HEADER in response)
        proxy_url = '{}/{}?token={}'.format(
            service_url,
            'tree',
            notebook_scheduler.get_notebook_token(project)
        )
        self.assertEqual(response[ProtectedView.NGINX_REDIRECT_HEADER], proxy_url)

    @mock.patch('schedulers.notebook_scheduler.NotebookSpawner')
    def test_redirects_to_proxy_protected_url_with_extra_path(self, spawner_mock):
        project = ProjectFactory(user=self.auth_client.user, has_notebook=True)
        deployment_name = DEPLOYMENT_NAME.format(
            project_uuid=project.uuid.hex, name=self.plugin_app)
        service_url = self._get_service_url(deployment_name=deployment_name)
        mock_instance = spawner_mock.return_value
        mock_instance.get_notebook_url.return_value = service_url

        # To `tree?`
        response = self.auth_client.get(self._get_url(project, 'tree?'))
        assert response.status_code == 200
        self.assertTrue(ProtectedView.NGINX_REDIRECT_HEADER in response)
        proxy_url = '{}/{}?token={}'.format(
            service_url,
            'tree',
            notebook_scheduler.get_notebook_token(project)
        )
        self.assertEqual(response[ProtectedView.NGINX_REDIRECT_HEADER], proxy_url)

        # To static files
        response = self.auth_client.get(
            self._get_url(project, 'static/components/something?v=4.7.0'))
        assert response.status_code == 200
        self.assertTrue(ProtectedView.NGINX_REDIRECT_HEADER in response)
        proxy_url = '{}/{}&token={}'.format(
            service_url,
            'static/components/something?v=4.7.0',
            notebook_scheduler.get_notebook_token(project)
        )
        self.assertEqual(response[ProtectedView.NGINX_REDIRECT_HEADER], proxy_url)


# Prevent this base class from running tests
del BaseTestPluginViewV1
