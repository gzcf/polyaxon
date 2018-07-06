# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging
import os
import random
import tarfile

from docker.errors import DockerException
from polyaxon_schemas.utils import SEARCH_METHODS

from dockerizer.builders import notebooks as notebooks_builder
from dockerizer.images import get_notebook_image_info
from experiments.models import Experiment
from experiments.tasks import build_experiment, stop_experiment
from libs.paths import delete_path
from polyaxon.celery_api import app as celery_app
from polyaxon.settings import CeleryTasks, Intervals
from projects.models import ExperimentGroup, Project
from projects.paths import get_project_data_path
from repos.models import Repo
from schedulers import notebook_scheduler, tensorboard_scheduler
from spawners.utils.constants import JobLifeCycle, ExperimentLifeCycle

logger = logging.getLogger('polyaxon.tasks.projects')


def _get_group_ro_retry(experiment_group_id, task):
    try:
        return ExperimentGroup.objects.get(id=experiment_group_id)
    except ExperimentGroup.DoesNotExist:
        logger.info('ExperimentGroup `{}` was not found.'.format(experiment_group_id))
        if task.request.retries < 2:
            logger.info('Trying again for ExperimentGroup `{}`.'.format(experiment_group_id))
            task.retry(countdown=Intervals.EXPERIMENTS_SCHEDULER)

        logger.info('Something went wrong, '
                    'the ExperimentGroup `{}` does not exist anymore.'.format(experiment_group_id))
        return None


@celery_app.task(name=CeleryTasks.EXPERIMENTS_GROUP_CREATE, bind=True, max_retries=None)
def create_group_experiments(self, experiment_group_id):
    experiment_group = _get_group_ro_retry(experiment_group_id=experiment_group_id, task=self)
    if not experiment_group:
        return

    # Parse polyaxonfile content and create the experiments
    specification = experiment_group.specification
    # We create a list of indices that we will explore
    if SEARCH_METHODS.is_sequential(specification.search_method):
        indices = range(specification.n_experiments or specification.matrix_space)
    elif SEARCH_METHODS.is_random(specification.search_method):
        sub_space = specification.n_experiments or specification.matrix_space
        indices = random.sample(range(specification.matrix_space), sub_space)
    else:
        logger.warning('Search method was not found `{}`'.format(specification.search_method))
        return
    for xp in indices:
        Experiment.objects.create(project=experiment_group.project,
                                  user=experiment_group.user,
                                  experiment_group=experiment_group,
                                  config=specification.parsed_data[xp])

    start_group_experiments.apply_async((experiment_group.id,), countdown=1)


@celery_app.task(name=CeleryTasks.EXPERIMENTS_GROUP_START, bind=True, max_retries=None)
def start_group_experiments(self, experiment_group_id):
    experiment_group = _get_group_ro_retry(experiment_group_id=experiment_group_id, task=self)
    if not experiment_group:
        return

    # Check for early stopping before starting new experiments from this group
    if experiment_group.should_stop_early():
        stop_group_experiments(experiment_group_id=experiment_group_id,
                               pending=True,
                               message='Early stopping')
        return

    experiment_to_start = experiment_group.n_experiments_to_start
    pending_experiments = experiment_group.pending_experiments[:experiment_to_start]
    n_pending_experiment = experiment_group.pending_experiments.count()

    for experiment in pending_experiments:
        build_experiment.delay(experiment_id=experiment.id)

    if n_pending_experiment - experiment_to_start > 0:
        # Schedule another task
        self.retry(countdown=Intervals.EXPERIMENTS_SCHEDULER)


@celery_app.task(name=CeleryTasks.EXPERIMENTS_GROUP_STOP_EXPERIMENTS)
def stop_group_experiments(experiment_group_id, pending, message=None):
    try:
        experiment_group = ExperimentGroup.objects.get(id=experiment_group_id)
    except ExperimentGroup.DoesNotExist:
        logger.info('ExperimentGroup `{}` was not found.'.format(experiment_group_id))
        return

    if pending:
        for experiment in experiment_group.pending_experiments:
            # Update experiment status to show that its stopped
            experiment.set_status(status=ExperimentLifeCycle.STOPPED, message=message)
    else:
        for experiment in experiment_group.experiments.exclude(
                experiment_status__status__in=ExperimentLifeCycle.DONE_STATUS).distinct():
            if experiment.is_running:
                stop_experiment.delay(experiment_id=experiment.id)
            else:
                # Update experiment status to show that its stopped
                experiment.set_status(status=ExperimentLifeCycle.STOPPED, message=message)


def get_valid_project(project_id):
    try:
        return Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        logger.info('Project id `{}` does not exist'.format(project_id))
        return None


@celery_app.task(name=CeleryTasks.PROJECTS_TENSORBOARD_START, ignore_result=True)
def start_tensorboard(project_id):
    project = get_valid_project(project_id)
    if not project or not project.tensorboard or project.has_tensorboard:
        return None
    tensorboard_scheduler.start_tensorboard(project)


@celery_app.task(name=CeleryTasks.PROJECTS_TENSORBOARD_STOP, ignore_result=True)
def stop_tensorboard(project_id):
    project = get_valid_project(project_id)
    if not project:
        return None
    tensorboard_scheduler.stop_tensorboard(project, update_status=True)


@celery_app.task(name=CeleryTasks.PROJECTS_NOTEBOOK_BUILD, ignore_result=True)
def build_notebook(project_id):
    project = get_valid_project(project_id)
    if not project or not project.notebook:
        return None

    job = project.notebook

    # Update job status to show that its building docker image
    job.set_status(JobLifeCycle.BUILDING, message='Building container')

    # Building the docker image
    try:
        status = notebooks_builder.build_notebook_job(project=project, job=project.notebook)
    except DockerException as e:
        logger.warning('Failed to build notebook %s', e)
        job.set_status(
            JobLifeCycle.FAILED,
            message='Failed to build image for notebook.'.format(project.unique_name))
        return
    except Repo.DoesNotExist:
        logger.warning('No code was found for this project')
        job.set_status(
            JobLifeCycle.FAILED,
            message='Failed to build image for notebook.'.format(project.unique_name))
        return

    if not status:
        return

    # Now we can start the notebook
    start_notebook.delay(project_id=project_id)


@celery_app.task(name=CeleryTasks.PROJECTS_NOTEBOOK_START, ignore_result=True)
def start_notebook(project_id):
    project = get_valid_project(project_id)
    if not project or not project.notebook or project.has_notebook:
        return None

    try:
        image_name, image_tag = get_notebook_image_info(project=project, job=project.notebook)
    except ValueError as e:
        logger.warning('Could not start the notebook, %s', e)
        return
    job_docker_image = '{}:{}'.format(image_name, image_tag)
    logger.info('Start notebook with built image `{}`'.format(job_docker_image))

    notebook_scheduler.start_notebook(project, image=job_docker_image)


@celery_app.task(name=CeleryTasks.PROJECTS_NOTEBOOK_STOP, ignore_result=True)
def stop_notebook(project_id):
    project = get_valid_project(project_id)
    if not project:
        return None

    notebook_scheduler.stop_notebook(project, update_status=True)


@celery_app.task(name=CeleryTasks.PROJECTS_HANDLE_DATA_UPLOAD, ignore_result=True)
def handle_new_data(project_id, tar_file_name):
    if not tarfile.is_tarfile(tar_file_name):
        raise ValueError('Received wrong file format.')

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        logger.warning('Repo with id `{}` does not exist anymore.'.format(project_id))
        return

    data_path = get_project_data_path(project.unique_name)
    logger.info('Extract tar file: tar_file_name=%s, data_path=%s', tar_file_name, data_path)

    os.makedirs(data_path, exist_ok=True)

    # clean the current path from all files
    path_files = os.listdir(data_path)
    for member in path_files:
        member = os.path.join(data_path, member)
        if os.path.isfile(member):
            os.remove(member)
        else:
            delete_path(member)

    # Untar the file
    with tarfile.open(tar_file_name) as tar:
        tar.extractall(data_path)

    # Delete the current tar
    os.remove(tar_file_name)
