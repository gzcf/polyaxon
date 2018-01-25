# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-25 13:23
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('version_api', django.contrib.postgres.fields.jsonb.JSONField(help_text='The cluster version api infos')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClusterEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField()),
                ('level', models.CharField(max_length=16)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='clusters.Cluster')),
            ],
        ),
        migrations.CreateModel(
            name='ClusterNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('sequence', models.IntegerField(editable=False, help_text='The sequence number of this node within the cluser.')),
                ('name', models.CharField(blank=True, help_text='Name of the node', max_length=256, null=True)),
                ('hostname', models.CharField(blank=True, max_length=256, null=True)),
                ('role', models.CharField(choices=[('master', 'master'), ('agent', 'agent')], help_text='The role of the node', max_length=6)),
                ('docker_version', models.CharField(blank=True, max_length=128, null=True)),
                ('kubelet_version', models.CharField(max_length=10)),
                ('os_image', models.CharField(max_length=128)),
                ('kernel_version', models.CharField(max_length=128)),
                ('schedulable_taints', models.BooleanField(default=False)),
                ('schedulable_state', models.BooleanField(default=False)),
                ('memory', models.BigIntegerField()),
                ('n_cpus', models.SmallIntegerField()),
                ('n_gpus', models.SmallIntegerField()),
                ('status', models.CharField(choices=[('UNKNOWN', 'UNKNOWN'), ('Ready', 'Ready'), ('NotReady', 'NotReady'), ('Deleted', 'Deleted')], default='UNKNOWN', max_length=24)),
                ('is_current', models.BooleanField(default=True)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nodes', to='clusters.Cluster')),
            ],
            options={
                'ordering': ['sequence'],
            },
        ),
        migrations.CreateModel(
            name='NodeGPU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('index', models.IntegerField()),
                ('serial', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('memory', models.BigIntegerField()),
                ('cluster_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gpus', to='clusters.ClusterNode')),
            ],
            options={
                'ordering': ['index'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='nodegpu',
            unique_together=set([('cluster_node', 'index')]),
        ),
        migrations.AlterUniqueTogether(
            name='clusternode',
            unique_together=set([('cluster', 'sequence')]),
        ),
    ]
