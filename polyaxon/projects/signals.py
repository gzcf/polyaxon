# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from libs.decorators import ignore_raw
from projects.models import ExperimentGroup, Project
from projects.tasks import create_group_experiments
from projects.paths import (
    delete_project_outputs,
    delete_experiment_group_outputs,
    delete_project_logs,
    delete_experiment_group_logs,
    delete_project_repos,
    delete_project_data, get_project_data_path)
from schedulers import experiment_scheduler, notebook_scheduler, tensorboard_scheduler


@receiver(post_save, sender=ExperimentGroup, dispatch_uid="experiment_group_saved")
@ignore_raw
def new_experiment_group(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs.get('created', False)

    if not created:
        return

    # Clean outputs and logs
    delete_experiment_group_outputs(instance.unique_name)
    delete_experiment_group_logs(instance.unique_name)

    create_group_experiments.apply_async((instance.id,), countdown=1)


@receiver(pre_delete, sender=ExperimentGroup, dispatch_uid="experiment_group_deleted")
@ignore_raw
def experiment_group_deleted(sender, **kwargs):
    """Stop all experiments before deleting the group."""

    instance = kwargs['instance']
    for experiment in instance.running_experiments:
        # Delete all jobs from DB before sending a signal to k8s,
        # this way no statuses will be updated in the meanwhile
        experiment.jobs.all().delete()
        experiment_scheduler.stop_experiment(experiment, update_status=False)

    # Delete outputs and logs
    delete_experiment_group_outputs(instance.unique_name)
    delete_experiment_group_logs(instance.unique_name)


@receiver(post_save, sender=Project, dispatch_uid="project_saved")
@ignore_raw
def new_project(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs.get('created', False)

    if not created:
        return

    # Clean outputs, logs, and repos
    unique_name = instance.unique_name
    delete_project_outputs(unique_name)
    delete_project_logs(unique_name)
    delete_project_repos(unique_name)
    delete_project_data(unique_name)

    os.makedirs(get_project_data_path(unique_name), exist_ok=True)


@receiver(pre_delete, sender=Project, dispatch_uid="project_deleted")
@ignore_raw
def project_deleted(sender, **kwargs):
    instance = kwargs['instance']
    tensorboard_scheduler.stop_tensorboard(instance, update_status=False)
    notebook_scheduler.stop_notebook(instance, update_status=False)
    # Delete tensorboard job
    if instance.tensorboard:
        instance.tensorboard.delete()

    # Delete notebook job
    if instance.notebook:
        instance.notebook.delete()

    # Clean outputs, logs, and repos
    unique_name = instance.unique_name
    delete_project_outputs(unique_name)
    delete_project_logs(unique_name)
    delete_project_repos(unique_name)
    delete_project_data(unique_name)
