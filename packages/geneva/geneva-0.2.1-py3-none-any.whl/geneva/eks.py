# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import base64
import logging
import tempfile
from datetime import datetime, timedelta

from kubernetes import client, config

from geneva.cluster import K8sConfigMethod

_LOG = logging.getLogger(__name__)

# Store a global singleton API client to reduce calls to STS/EKS
_KUBE_API_CLIENT: client.ApiClient | None = None

# Default EKS token expiration period in seconds (30mins)
TOKEN_EXPIRATION_S = 1800


def build_api_client(
    config_method: K8sConfigMethod,
    region: str | None = "us-east-1",
    cluster_name: str = "lancedb",
    role_name: str = "geneva-client-role",
    refresh: bool = False,
) -> client.ApiClient | None:
    """Build the k8s API client based on the configuration method and region.
    The client is cached in a global variable to minimize expensive EKS calls.
    Returns None for default config method (non-EKS).
    """
    global _KUBE_API_CLIENT

    # Return cached client if available
    if _KUBE_API_CLIENT is not None and not refresh:
        return _KUBE_API_CLIENT

    if config_method == K8sConfigMethod.IN_CLUSTER:
        config.load_incluster_config()

        return None
    elif config_method == K8sConfigMethod.LOCAL:
        config.load_kube_config()

        return None
    elif config_method == K8sConfigMethod.EKS_AUTH:
        ca_data, endpoint, token = _eks_auth(cluster_name, region, role_name)
        cafile = _write_cafile(ca_data)
        _KUBE_API_CLIENT = _api_client(endpoint, token, cafile.name)
        return _KUBE_API_CLIENT
    else:
        raise Exception(f"unsupported config method: {config_method}")


def _eks_auth(cluster_name: str, region: str, role_name: str) -> (str, str, str):
    import boto3

    eks_client = boto3.client("eks", region_name=region)
    identity = boto3.client("sts", region_name=region).get_caller_identity()
    _LOG.debug("caller identity: %s", identity)
    acct_id = identity.get("Account")
    # this role requires an EKS Access Entry with
    # AmazonEKSClusterAdminPolicy on the given namespace
    # and must be assumable by the current user
    role_arn = f"arn:aws:iam::{acct_id}:role/{role_name}"
    token = get_token(cluster_name, role_arn, region, TOKEN_EXPIRATION_S)["status"][
        "token"
    ]
    cluster_data = eks_client.describe_cluster(name=cluster_name)["cluster"]
    ca_data = cluster_data["certificateAuthority"]["data"]
    endpoint = cluster_data["endpoint"]
    _LOG.info(f"authenticated with EKS. {cluster_name=} {role_arn=}")

    return ca_data, endpoint, token


def _write_cafile(data: str) -> tempfile.NamedTemporaryFile:
    # ruff: noqa: SIM115
    cafile = tempfile.NamedTemporaryFile(delete=False)
    cadata_b64 = data
    cadata = base64.b64decode(cadata_b64)
    cafile.write(cadata)
    cafile.flush()
    return cafile


def _api_client(endpoint: str, token: str, cafile: str) -> client.ApiClient:
    kconfig = config.kube_config.Configuration(
        host=endpoint, api_key={"authorization": "Bearer " + token}
    )
    kconfig.ssl_ca_cert = cafile
    kclient = client.ApiClient(configuration=kconfig)
    return kclient


def _get_expiration_time(token_expiration_s: int) -> str:
    token_expiration = datetime.utcnow() + timedelta(seconds=token_expiration_s)
    return token_expiration.strftime("%Y-%m-%dT%H:%M:%SZ")


def _get_exp_s() -> int:
    return TOKEN_EXPIRATION_S


def get_token(
    cluster_name: str,
    role_arn: str = None,
    region_name: str = None,
    token_expiration_s: int = _get_exp_s(),
) -> dict:
    from awscli.customizations.eks.get_token import (
        STSClientFactory,
        TokenGenerator,
    )
    from botocore import session

    work_session = session.get_session()
    client_factory = STSClientFactory(work_session)
    sts_client = client_factory.get_sts_client(
        role_arn=role_arn, region_name=region_name
    )
    token = TokenGenerator(sts_client).get_token(cluster_name)
    return {
        "kind": "ExecCredential",
        "apiVersion": "client.authentication.k8s.io/v1beta1",
        "spec": {},
        "status": {
            "expirationTimestamp": _get_expiration_time(token_expiration_s),
            "token": token,
        },
    }
