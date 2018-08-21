# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from rest_framework import serializers, fields

from libs.spec_validation import validate_tensorboard_spec_content
from plugins.models import TensorboardJob, NotebookJob


class PluginJobBaseSerializer(serializers.ModelSerializer):
    user = fields.SerializerMethodField()
    project_name = fields.SerializerMethodField()
    resources = fields.SerializerMethodField()

    class Meta:
        fields = ('user', 'content', 'config', 'created_at', 'last_status', 'resources', 'project_name')

    def get_user(self, obj):
        return obj.user.username

    def get_project_name(self, obj):
        return obj.project.unique_name

    def get_resources(self, obj):
        resources = obj.resources
        if resources and not isinstance(resources, dict):
            resources = resources.to_dict()
        return resources

    def _validate_spec(self, values):
        # content is optional
        if not values:
            return values

        validate_tensorboard_spec_content(values)

        # Resume normal creation
        return values

    def validate_content(self, content):
        return self._validate_spec(content)

    def validate_config(self, config):
        return self._validate_spec(config)


class TensorboardJobSerializer(PluginJobBaseSerializer):
    class Meta(PluginJobBaseSerializer.Meta):
        model = TensorboardJob


class NotebookJobSerializer(PluginJobBaseSerializer):
    class Meta(PluginJobBaseSerializer.Meta):
        model = NotebookJob
