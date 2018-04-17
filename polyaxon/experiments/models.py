# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging
import uuid

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.functional import cached_property

from polyaxon_schemas.polyaxonfile.specification import Specification
from polyaxon_schemas.utils import TaskType

from jobs.models import Job, JobStatus, JobResources
from libs.models import DiffModel, DescribableModel
from libs.spec_validation import validate_spec_content
from spawners.utils.constants import JobLifeCycle, ExperimentLifeCycle

logger = logging.getLogger('polyaxon.experiments')


class Experiment(DiffModel, DescribableModel):
    """A model that represents experiments."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        null=False)
    sequence = models.IntegerField(
        editable=False,
        null=False,
        help_text='The sequence number of this experiment within the project.', )
    project = models.ForeignKey(
        'projects.Project',
        related_name='experiments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='experiments')
    experiment_group = models.ForeignKey(
        'projects.ExperimentGroup',
        blank=True,
        null=True,
        related_name='experiments',
        help_text='The experiment group that generate this experiment.')
    content = models.TextField(
        blank=True,
        null=True,
        help_text='[Deprecated] The yaml content of the polyaxonfile/specification.')
    config = JSONField(
        help_text='The compiled polyaxon with specific values for this experiment.',
        validators=[validate_spec_content])
    original_experiment = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='clones',
        help_text='The original experiment that was cloned from.')
    experiment_status = models.OneToOneField(
        'ExperimentStatus',
        related_name='+',
        blank=True,
        null=True,
        editable=True,
        on_delete=models.SET_NULL)
    experiment_metric = models.OneToOneField(
        'ExperimentMetric',
        related_name='+',
        blank=True,
        null=True,
        editable=True,
        on_delete=models.SET_NULL)
    commit = models.CharField(
        max_length=40,
        blank=True,
        null=True)

    class Meta:
        ordering = ['sequence']
        unique_together = (('project', 'sequence'),)

    def save(self, *args, **kwargs):
        if self.pk is None:
            last = Experiment.objects.filter(project=self.project).last()
            self.sequence = 1
            if last:
                self.sequence = last.sequence + 1

        super(Experiment, self).save(*args, **kwargs)

    def __str__(self):
        return self.unique_name

    @property
    def unique_name(self):
        if self.experiment_group:
            return '{}.{}'.format(self.experiment_group.unique_name, self.sequence)
        return '{}.{}'.format(self.project.unique_name, self.sequence)

    @cached_property
    def compiled_spec(self):
        return Specification(experiment=self.uuid, values=self.config)

    @cached_property
    def declarations(self):
        return self.compiled_spec.declarations

    @cached_property
    def resources(self):
        return self.compiled_spec.total_resources

    @property
    def last_job_statuses(self):
        """The statuses of the job in this experiment."""
        statuses = []
        for job in self.jobs.all():
            status = job.last_status
            if status is not None:
                statuses.append(status)
        return statuses

    @property
    def calculated_status(self):
        master_status = self.jobs.filter(role=TaskType.MASTER)[0].last_status
        calculated_status = master_status if JobLifeCycle.is_done(master_status) else None
        if calculated_status is None:
            calculated_status = ExperimentLifeCycle.jobs_status(self.last_job_statuses)
        if calculated_status is None:
            return self.last_status
        return calculated_status

    @property
    def last_status(self):
        return self.experiment_status.status if self.experiment_status else None

    @property
    def last_metric(self):
        return self.experiment_metric.values if self.experiment_metric else None

    @property
    def is_running(self):
        return ExperimentLifeCycle.is_running(self.last_status)

    @property
    def is_done(self):
        return ExperimentLifeCycle.is_done(self.last_status)

    @property
    def finished_at(self):
        status = self.statuses.filter(status__in=ExperimentLifeCycle.DONE_STATUS).first()
        if status:
            return status.created_at
        return None

    @property
    def started_at(self):
        status = self.statuses.filter(status=ExperimentLifeCycle.STARTING).first()
        if status:
            return status.created_at
        return None

    @property
    def is_clone(self):
        return self.original_experiment is not None

    @property
    def is_independent(self):
        """If the experiment belongs to a experiment_group or is independently created."""
        return self.experiment_group is None

    def update_status(self):
        current_status = self.last_status
        calculated_status = self.calculated_status
        if calculated_status != current_status:
            # Add new status to the experiment
            self.set_status(calculated_status)
            return True
        return False

    def set_status(self, status, message=None):
        ExperimentStatus.objects.create(experiment=self, status=status, message=message)


class ExperimentStatus(models.Model):
    """A model that represents an experiment status at certain time."""
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        null=False)
    experiment = models.ForeignKey(Experiment, related_name='statuses')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        default=ExperimentLifeCycle.CREATED,
        choices=ExperimentLifeCycle.CHOICES)
    message = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Experiment Statuses'
        ordering = ['created_at']

    def __str__(self):
        return '{} <{}>'.format(self.experiment.unique_name, self.status)


class ExperimentMetric(models.Model):
    """A model that represents an experiment metric at certain time."""
    experiment = models.ForeignKey(Experiment, related_name='metrics')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    values = JSONField()

    def __str__(self):
        return '{} <{}>'.format(self.experiment.unique_name, self.created_at)

    class Meta:
        ordering = ['created_at']


class ExperimentJob(Job):
    """A model that represents job related to an experiment"""
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        null=False)
    experiment = models.ForeignKey(Experiment, related_name='jobs')
    definition = JSONField(help_text='The specific values for this job.')
    role = models.CharField(max_length=64, default=TaskType.MASTER)
    sequence = models.IntegerField(
        editable=False,
        null=False,
        help_text='The sequence number of this job within the experiment.', )
    resources = models.OneToOneField(
        JobResources,
        related_name='+',
        blank=True,
        null=True,
        editable=True,
        on_delete=models.SET_NULL)
    job_status = models.OneToOneField(
        'ExperimentJobStatus',
        related_name='+',
        blank=True,
        null=True,
        editable=True,
        on_delete=models.SET_NULL)

    class Meta:
        ordering = ['sequence']
        unique_together = (('experiment', 'sequence'),)

    def __str__(self):
        return self.unique_name

    @property
    def unique_name(self):
        return '{}.{}.{}'.format(self.experiment.unique_name, self.sequence, self.role)

    def save(self, *args, **kwargs):
        if self.pk is None:
            last = ExperimentJob.objects.filter(experiment=self.experiment).last()
            self.sequence = 1
            if last:
                self.sequence = last.sequence + 1

        super(ExperimentJob, self).save(*args, **kwargs)

    def set_status(self, status, message=None, details=None):
        return self._set_status(status_model=ExperimentJobStatus,
                                logger=logger,
                                status=status,
                                message=message,
                                details=details)


class ExperimentJobStatus(JobStatus):
    """A model that represents job status at certain time."""
    job = models.ForeignKey(ExperimentJob, related_name='statuses')

    class Meta(JobStatus.Meta):
        verbose_name_plural = 'Experiment Job Statuses'
