# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from kubernetes import client

from polyaxon_k8s import constants as k8s_constants

from libs.utils import get_list
from spawners.templates import constants
from spawners.templates import pods


def get_labels(app, project_name, project_uuid, role=None, type=None):
    labels = {'app': app, 'project_name': project_name, 'project_uuid': project_uuid}
    if role:
        labels['role'] = role
    if type:
        labels['type'] = type
    return labels


def get_project_pod_spec(volume_mounts,
                         volumes,
                         image,
                         container_name=None,
                         command=None,
                         args=None,
                         ports=None,
                         resources=None,
                         env_vars=None,
                         restart_policy=None):
    """Pod spec to be used to create pods for project side: tensorboard, notebooks."""
    volume_mounts = get_list(volume_mounts)
    volumes = get_list(volumes)

    gpu_volume_mounts, gpu_volumes = pods.get_gpu_volumes_def(resources)
    volume_mounts += gpu_volume_mounts
    volumes += gpu_volumes

    env_vars = get_list(env_vars)
    env_vars += pods.get_resources_env_vars(resources)

    ports = [client.V1ContainerPort(container_port=port) for port in ports]

    containers = [client.V1Container(name=container_name,
                                     image=image,
                                     command=command,
                                     args=args,
                                     ports=ports,
                                     env=env_vars,
                                     resources=pods.get_resources(resources),
                                     volume_mounts=volume_mounts)]
    return client.V1PodSpec(restart_policy=restart_policy, containers=containers, volumes=volumes)


def get_deployment_spec(namespace,
                        app,
                        name,
                        project_name,
                        project_uuid,
                        volume_mounts,
                        volumes,
                        image,
                        command,
                        args,
                        ports,
                        container_name=None,
                        resources=None,
                        role=None,
                        type=None,
                        replicas=1):
    labels = get_labels(app=app,
                        project_name=project_name,
                        project_uuid=project_uuid,
                        role=role,
                        type=type)
    metadata = client.V1ObjectMeta(
        name=constants.DEPLOYMENT_NAME.format(name=name, project_uuid=project_uuid),
        labels=labels,
        namespace=namespace)
    pod_spec = get_project_pod_spec(volume_mounts=volume_mounts,
                                    volumes=volumes,
                                    image=image,
                                    container_name=container_name,
                                    command=command,
                                    args=args,
                                    resources=resources,
                                    ports=ports)
    template_spec = client.V1PodTemplateSpec(metadata=metadata, spec=pod_spec)
    return client.AppsV1beta1DeploymentSpec(replicas=replicas, template=template_spec)


def get_deployment(namespace,
                   app,
                   name,
                   project_name,
                   project_uuid,
                   volume_mounts,
                   volumes,
                   image,
                   command,
                   args,
                   ports,
                   container_name,
                   resources=None,
                   role=None,
                   type=None,
                   replicas=1):
    labels = get_labels(app=app,
                        project_name=project_name,
                        project_uuid=project_uuid,
                        role=role,
                        type=type)
    metadata = client.V1ObjectMeta(
        name=constants.DEPLOYMENT_NAME.format(project_uuid=project_uuid, name=name),
        labels=labels,
        namespace=namespace)
    spec = get_deployment_spec(namespace=namespace,
                               app=app,
                               name=name,
                               project_name=project_name,
                               project_uuid=project_uuid,
                               volume_mounts=volume_mounts,
                               volumes=volumes,
                               image=image,
                               command=command,
                               args=args,
                               ports=ports,
                               container_name=container_name,
                               resources=resources,
                               role=role,
                               type=type,
                               replicas=replicas)
    return client.AppsV1beta1Deployment(api_version=k8s_constants.K8S_API_VERSION_V1_BETA1,
                                        kind=k8s_constants.K8S_DEPLOYMENT_KIND,
                                        metadata=metadata,
                                        spec=spec)
