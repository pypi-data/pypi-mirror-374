from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.patch_remote_cluster_body import PatchRemoteClusterBody
from ...models.remote_cluster import RemoteCluster
from ...types import Response


def _get_kwargs(
    remote_id: str,
    *,
    body: PatchRemoteClusterBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/api/v4/remotecluster/{remote_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, RemoteCluster]]:
    if response.status_code == 200:
        response_200 = RemoteCluster.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, RemoteCluster]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    remote_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchRemoteClusterBody,
) -> Response[Union[AppError, RemoteCluster]]:
    """Patch a remote cluster.

     Partially update a Remote Cluster by providing only the fields you want to update. Ommited fields
    will not be updated.

    ##### Permissions
    `manage_secure_connections`

    Args:
        remote_id (str):
        body (PatchRemoteClusterBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, RemoteCluster]]
    """

    kwargs = _get_kwargs(
        remote_id=remote_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    remote_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchRemoteClusterBody,
) -> Optional[Union[AppError, RemoteCluster]]:
    """Patch a remote cluster.

     Partially update a Remote Cluster by providing only the fields you want to update. Ommited fields
    will not be updated.

    ##### Permissions
    `manage_secure_connections`

    Args:
        remote_id (str):
        body (PatchRemoteClusterBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, RemoteCluster]
    """

    return sync_detailed(
        remote_id=remote_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    remote_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchRemoteClusterBody,
) -> Response[Union[AppError, RemoteCluster]]:
    """Patch a remote cluster.

     Partially update a Remote Cluster by providing only the fields you want to update. Ommited fields
    will not be updated.

    ##### Permissions
    `manage_secure_connections`

    Args:
        remote_id (str):
        body (PatchRemoteClusterBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, RemoteCluster]]
    """

    kwargs = _get_kwargs(
        remote_id=remote_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    remote_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchRemoteClusterBody,
) -> Optional[Union[AppError, RemoteCluster]]:
    """Patch a remote cluster.

     Partially update a Remote Cluster by providing only the fields you want to update. Ommited fields
    will not be updated.

    ##### Permissions
    `manage_secure_connections`

    Args:
        remote_id (str):
        body (PatchRemoteClusterBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, RemoteCluster]
    """

    return (
        await asyncio_detailed(
            remote_id=remote_id,
            client=client,
            body=body,
        )
    ).parsed
