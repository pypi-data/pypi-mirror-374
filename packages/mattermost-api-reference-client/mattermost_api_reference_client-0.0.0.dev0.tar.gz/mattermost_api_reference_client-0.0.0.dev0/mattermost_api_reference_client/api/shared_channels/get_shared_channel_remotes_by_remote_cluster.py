from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.shared_channel_remote import SharedChannelRemote
from ...types import UNSET, Response, Unset


def _get_kwargs(
    remote_id: str,
    *,
    include_unconfirmed: Union[Unset, bool] = UNSET,
    exclude_confirmed: Union[Unset, bool] = UNSET,
    exclude_home: Union[Unset, bool] = UNSET,
    exclude_remote: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_unconfirmed"] = include_unconfirmed

    params["exclude_confirmed"] = exclude_confirmed

    params["exclude_home"] = exclude_home

    params["exclude_remote"] = exclude_remote

    params["include_deleted"] = include_deleted

    params["page"] = page

    params["per_page"] = per_page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/remotecluster/{remote_id}/sharedchannelremotes",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["SharedChannelRemote"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = SharedChannelRemote.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, list["SharedChannelRemote"]]]:
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
    include_unconfirmed: Union[Unset, bool] = UNSET,
    exclude_confirmed: Union[Unset, bool] = UNSET,
    exclude_home: Union[Unset, bool] = UNSET,
    exclude_remote: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
) -> Response[Union[AppError, list["SharedChannelRemote"]]]:
    """Get shared channel remotes by remote cluster.

     Get a list of the channels shared with a given remote cluster
    and their status.

    ##### Permissions
    `manage_secure_connections`

    Args:
        remote_id (str):
        include_unconfirmed (Union[Unset, bool]):
        exclude_confirmed (Union[Unset, bool]):
        exclude_home (Union[Unset, bool]):
        exclude_remote (Union[Unset, bool]):
        include_deleted (Union[Unset, bool]):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['SharedChannelRemote']]]
    """

    kwargs = _get_kwargs(
        remote_id=remote_id,
        include_unconfirmed=include_unconfirmed,
        exclude_confirmed=exclude_confirmed,
        exclude_home=exclude_home,
        exclude_remote=exclude_remote,
        include_deleted=include_deleted,
        page=page,
        per_page=per_page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    remote_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_unconfirmed: Union[Unset, bool] = UNSET,
    exclude_confirmed: Union[Unset, bool] = UNSET,
    exclude_home: Union[Unset, bool] = UNSET,
    exclude_remote: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
) -> Optional[Union[AppError, list["SharedChannelRemote"]]]:
    """Get shared channel remotes by remote cluster.

     Get a list of the channels shared with a given remote cluster
    and their status.

    ##### Permissions
    `manage_secure_connections`

    Args:
        remote_id (str):
        include_unconfirmed (Union[Unset, bool]):
        exclude_confirmed (Union[Unset, bool]):
        exclude_home (Union[Unset, bool]):
        exclude_remote (Union[Unset, bool]):
        include_deleted (Union[Unset, bool]):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['SharedChannelRemote']]
    """

    return sync_detailed(
        remote_id=remote_id,
        client=client,
        include_unconfirmed=include_unconfirmed,
        exclude_confirmed=exclude_confirmed,
        exclude_home=exclude_home,
        exclude_remote=exclude_remote,
        include_deleted=include_deleted,
        page=page,
        per_page=per_page,
    ).parsed


async def asyncio_detailed(
    remote_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_unconfirmed: Union[Unset, bool] = UNSET,
    exclude_confirmed: Union[Unset, bool] = UNSET,
    exclude_home: Union[Unset, bool] = UNSET,
    exclude_remote: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
) -> Response[Union[AppError, list["SharedChannelRemote"]]]:
    """Get shared channel remotes by remote cluster.

     Get a list of the channels shared with a given remote cluster
    and their status.

    ##### Permissions
    `manage_secure_connections`

    Args:
        remote_id (str):
        include_unconfirmed (Union[Unset, bool]):
        exclude_confirmed (Union[Unset, bool]):
        exclude_home (Union[Unset, bool]):
        exclude_remote (Union[Unset, bool]):
        include_deleted (Union[Unset, bool]):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['SharedChannelRemote']]]
    """

    kwargs = _get_kwargs(
        remote_id=remote_id,
        include_unconfirmed=include_unconfirmed,
        exclude_confirmed=exclude_confirmed,
        exclude_home=exclude_home,
        exclude_remote=exclude_remote,
        include_deleted=include_deleted,
        page=page,
        per_page=per_page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    remote_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    include_unconfirmed: Union[Unset, bool] = UNSET,
    exclude_confirmed: Union[Unset, bool] = UNSET,
    exclude_home: Union[Unset, bool] = UNSET,
    exclude_remote: Union[Unset, bool] = UNSET,
    include_deleted: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    per_page: Union[Unset, int] = UNSET,
) -> Optional[Union[AppError, list["SharedChannelRemote"]]]:
    """Get shared channel remotes by remote cluster.

     Get a list of the channels shared with a given remote cluster
    and their status.

    ##### Permissions
    `manage_secure_connections`

    Args:
        remote_id (str):
        include_unconfirmed (Union[Unset, bool]):
        exclude_confirmed (Union[Unset, bool]):
        exclude_home (Union[Unset, bool]):
        exclude_remote (Union[Unset, bool]):
        include_deleted (Union[Unset, bool]):
        page (Union[Unset, int]):
        per_page (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['SharedChannelRemote']]
    """

    return (
        await asyncio_detailed(
            remote_id=remote_id,
            client=client,
            include_unconfirmed=include_unconfirmed,
            exclude_confirmed=exclude_confirmed,
            exclude_home=exclude_home,
            exclude_remote=exclude_remote,
            include_deleted=include_deleted,
            page=page,
            per_page=per_page,
        )
    ).parsed
