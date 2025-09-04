# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import functools
import logging
from collections.abc import Callable
from typing import Any

import attrs
import kubernetes
from kubernetes import client
from kubernetes.client import ApiException

from geneva.cluster import K8sConfigMethod
from geneva.eks import build_api_client

_LOG = logging.getLogger(__name__)


def _refresh_auth_for_kuberay(kuberay_clients_instance) -> Callable:
    """Create a refresh_auth decorator for KuberayClients methods"""

    def decorator(func) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retry_count = 0

            while retry_count <= 2:
                try:
                    return func(*args, **kwargs)
                except ApiException as e:  # noqa: PERF203
                    if e.status != 401:
                        raise e
                    if retry_count >= 2:
                        _LOG.error("k8s auth retries exceeded")
                        raise e

                    _LOG.info("token expired, reauthenticating with k8s")
                    kuberay_clients_instance.refresh()
                    retry_count += 1
            return None

        return wrapper

    return decorator


def _wrap_api_methods(api_instance: Any, kuberay_clients_instance: Any) -> Any:
    """Wrap all methods of an API instance with refresh_auth decorator"""
    decorator = _refresh_auth_for_kuberay(kuberay_clients_instance)

    for attr_name in dir(api_instance):
        if (
            not attr_name.startswith("_")
            and attr_name != "connect_get_namespaced_pod_portforward"
        ):
            attr = getattr(api_instance, attr_name)
            if callable(attr):
                wrapped_attr = decorator(attr)
                setattr(api_instance, attr_name, wrapped_attr)
    return api_instance


@attrs.define()
class KuberayClients:
    """
    Wrap kubernetes clients required for Kuberay operations
    """

    core_api: client.CoreV1Api = attrs.field(init=False)
    custom_api: client.CustomObjectsApi = attrs.field(init=False)
    auth_api: client.AuthorizationV1Api = attrs.field(init=False)
    scheduling_api: client.SchedulingV1Api = attrs.field(init=False)

    config_method: K8sConfigMethod = attrs.field(default=K8sConfigMethod.LOCAL)
    """
    Method to retrieve kubeconfig
    """

    region: str = attrs.field(
        default=None,
    )
    """
    Optional cloud region where the cluster is located
    """

    cluster_name: str = attrs.field(
        default=None,
    )
    """
    Optional k8s cluster name, required for EKS auth
    """

    role_name: str = attrs.field(
        default=None,
    )
    """
    Optional IAM role name, required for EKS auth
    """

    def __attrs_post_init__(self) -> None:
        self.init_clients(False)

    def refresh(self) -> None:
        self.init_clients(True)

    def init_clients(self, refresh: bool) -> None:
        # Initialize API clients based on config_method
        # If refresh is set, it will re-authenticate instead of using cached client
        client = build_api_client(
            self.config_method, self.region, self.cluster_name, self.role_name, refresh
        )

        # Create API clients
        self.custom_api = kubernetes.client.CustomObjectsApi(api_client=client)
        self.core_api = kubernetes.client.CoreV1Api(api_client=client)
        self.auth_api = kubernetes.client.AuthorizationV1Api(api_client=client)
        self.scheduling_api = kubernetes.client.SchedulingV1Api(api_client=client)

        # Wrap all API methods with refresh_auth decorator
        _wrap_api_methods(self.custom_api, self)
        _wrap_api_methods(self.core_api, self)
        _wrap_api_methods(self.auth_api, self)
        _wrap_api_methods(self.scheduling_api, self)
