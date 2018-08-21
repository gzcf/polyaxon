# -*- coding: utf-8 -*-
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from plugins import views

urlpatterns = [
    url(r'^notebook_jobs/?$',
        views.NotebookJobListView.as_view()),
    url(r'^tensorboard_jobs/?$',
        views.TensorboardJobListView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
