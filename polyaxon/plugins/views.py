# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from django.conf import settings
from django.db import transaction
from django.http import Http404
from rest_framework import status, filters
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from libs.utils import to_bool
from libs.views import ProtectedView
from plugins.models import NotebookJob, TensorboardJob
from plugins.serializers import TensorboardJobSerializer, NotebookJobSerializer
from projects.models import Project
from projects.permissions import IsProjectOwnerOrPublicReadOnly, get_permissible_project
from projects.tasks import start_tensorboard, stop_tensorboard, build_notebook, stop_notebook
from repos import git
from schedulers import notebook_scheduler, tensorboard_scheduler
from spawners.utils.constants import ExperimentLifeCycle, JobLifeCycle


class PluginJobListView(ListAPIView):
    permission_classes = (AllowAny,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('created_at', 'project__name', 'user__username')

    def get_queryset(self):
        print('PluginJobListView')
        queryset = self.queryset
        is_running = to_bool(self.request.query_params.get('is_running', False))
        if is_running:
            queryset = queryset.filter(job_status__status__in=JobLifeCycle.RUNNING_STATUS)

        return queryset


class NotebookJobListView(PluginJobListView):
    queryset = NotebookJob.objects.all()
    serializer_class = NotebookJobSerializer


class TensorboardJobListView(PluginJobListView):
    queryset = TensorboardJob.objects.all()
    serializer_class = TensorboardJobSerializer


class StartTensorboardView(CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = TensorboardJobSerializer
    permission_classes = (IsAuthenticated, IsProjectOwnerOrPublicReadOnly)
    lookup_field = 'name'

    def filter_queryset(self, queryset):
        username = self.kwargs['username']
        return queryset.filter(user__username=username)

    @staticmethod
    def _get_default_tensorboard_config(project):
        return {
            'config': {
                'version': 1,
                'project': {'name': project.name},
                'run': {'image': settings.TENSORBOARD_DOCKER_IMAGE}
            }
        }

    def _should_create_tensorboard_job(self, project):
        # If the project already has a tensorboard specification
        # and no data is provided to update
        # then we do not need to create a TensorboardJob
        if project.tensorboard and not self.request.data:
            return False
        return True

    def _create_tensorboard(self, project):
        if not self._should_create_tensorboard_job(project):
            return
        config = self.request.data or self._get_default_tensorboard_config(project)
        serializer = self.get_serializer(instance=project.tensorboard, data=config)
        serializer.is_valid(raise_exception=True)
        project.tensorboard = serializer.save(user=self.request.user, project=project)
        project.save()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.has_tensorboard:
            self._create_tensorboard(obj)
            if not obj.tensorboard.is_running:
                transaction.on_commit(lambda: start_tensorboard.delay(project_id=obj.id))
        return Response(status=status.HTTP_200_OK)


class StopTensorboardView(CreateAPIView):
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated, IsProjectOwnerOrPublicReadOnly)
    lookup_field = 'name'

    def filter_queryset(self, queryset):
        username = self.kwargs['username']
        return queryset.filter(user__username=username)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.has_tensorboard:
            stop_tensorboard.delay(project_id=obj.id)
        return Response(status=status.HTTP_200_OK)


class StartNotebookView(CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = NotebookJobSerializer
    permission_classes = (IsAuthenticated, IsProjectOwnerOrPublicReadOnly)
    lookup_field = 'name'

    def filter_queryset(self, queryset):
        username = self.kwargs['username']
        return queryset.filter(user__username=username)

    def _should_create_notebook_job(self, project):
        # If the project already has a notebook specification
        # and no data is provided to update
        # then we do not need to create a TensorboardJob
        if project.notebook and not self.request.data:
            return False
        return True

    def _create_notebook(self, project):
        if not self._should_create_notebook_job(project):
            return
        serializer = self.get_serializer(instance=project.notebook, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        project.notebook = serializer.save(user=self.request.user, project=project)
        project.save()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.has_notebook:
            self._create_notebook(obj)
            if not obj.notebook.is_running:
                transaction.on_commit(lambda: build_notebook.delay(project_id=obj.id))

        return Response(status=status.HTTP_200_OK)


class StopNotebookView(CreateAPIView):
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated, IsProjectOwnerOrPublicReadOnly)
    lookup_field = 'name'

    def filter_queryset(self, queryset):
        username = self.kwargs['username']
        return queryset.filter(user__username=username)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.has_notebook:
            commit = request.data.get('commit')
            commit = to_bool(commit) if commit is not None else True
            if commit:
                # Commit changes
                git.commit(obj.repo.path, request.user.email, request.user.username)
            else:
                # Reset changes
                git.undo(obj.repo.path)
            stop_notebook.delay(project_id=obj.id)
        elif obj.notebook and obj.notebook.is_running:
            obj.notebook.set_status(status=ExperimentLifeCycle.STOPPED,
                                    message='Notebook was stopped')
        return Response(status=status.HTTP_200_OK)


class PluginJobView(ProtectedView):
    @staticmethod
    def get_base_path(project):
        return ''

    @staticmethod
    def get_base_params(project):
        return ''

    def has_plugin_job(self, project):
        raise NotImplementedError

    def get_service_url(self, project):
        raise NotImplementedError

    def get_object(self):
        return get_permissible_project(view=self)

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        if not self.has_plugin_job(project):
            raise Http404
        service_url = self.get_service_url(project=project)
        path = '/{}'.format(service_url.strip('/'))
        base_path = self.get_base_path(project)
        base_params = self.get_base_params(project)
        if self.kwargs['path']:
            path = '{}/{}'.format(path, self.kwargs['path'].strip('/'))
        elif base_path:
            path = '{}/{}'.format(path, base_path)
        if request.GET:
            path = '{}?{}'.format(path, request.GET.urlencode())
            if base_params:
                path = '{}&{}'.format(path, base_params)
        elif base_params:
            path = '{}?{}'.format(path, base_params)
        else:
            path = path + '/'
        return self.redirect(path=path)


class NotebookView(PluginJobView):
    @staticmethod
    def get_base_path(project):
        return 'tree'

    @staticmethod
    def get_base_params(project):
        return 'token={}'.format(notebook_scheduler.get_notebook_token(project=project))

    def get_service_url(self, project):
        return notebook_scheduler.get_notebook_url(project=project)

    def has_plugin_job(self, project):
        return project.has_notebook


class TensorboardView(PluginJobView):
    def get_service_url(self, project):
        return tensorboard_scheduler.get_tensorboard_url(project=project)

    def has_plugin_job(self, project):
        return project.has_tensorboard
