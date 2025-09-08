from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.update_channel_bookmark_body import UpdateChannelBookmarkBody
from ...models.update_channel_bookmark_response import UpdateChannelBookmarkResponse
from ...types import Response


def _get_kwargs(
    channel_id: str,
    bookmark_id: str,
    *,
    body: UpdateChannelBookmarkBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/api/v4/channels/{channel_id}/bookmarks/{bookmark_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, UpdateChannelBookmarkResponse]]:
    if response.status_code == 200:
        response_200 = UpdateChannelBookmarkResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

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
) -> Response[Union[AppError, UpdateChannelBookmarkResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str,
    bookmark_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateChannelBookmarkBody,
) -> Response[Union[AppError, UpdateChannelBookmarkResponse]]:
    """Update channel bookmark

     Partially update a channel bookmark by providing only the
    fields you want to update. Ommited fields will not be
    updated. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored.

    __Minimum server version__: 9.5

    ##### Permissions
    Must have the `edit_bookmark_public_channel` or
    `edit_bookmark_private_channel` depending on the channel
    type. If the channel is a DM or GM, must be a non-guest
    member.

    Args:
        channel_id (str):
        bookmark_id (str):
        body (UpdateChannelBookmarkBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UpdateChannelBookmarkResponse]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        bookmark_id=bookmark_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str,
    bookmark_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateChannelBookmarkBody,
) -> Optional[Union[AppError, UpdateChannelBookmarkResponse]]:
    """Update channel bookmark

     Partially update a channel bookmark by providing only the
    fields you want to update. Ommited fields will not be
    updated. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored.

    __Minimum server version__: 9.5

    ##### Permissions
    Must have the `edit_bookmark_public_channel` or
    `edit_bookmark_private_channel` depending on the channel
    type. If the channel is a DM or GM, must be a non-guest
    member.

    Args:
        channel_id (str):
        bookmark_id (str):
        body (UpdateChannelBookmarkBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UpdateChannelBookmarkResponse]
    """

    return sync_detailed(
        channel_id=channel_id,
        bookmark_id=bookmark_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    channel_id: str,
    bookmark_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateChannelBookmarkBody,
) -> Response[Union[AppError, UpdateChannelBookmarkResponse]]:
    """Update channel bookmark

     Partially update a channel bookmark by providing only the
    fields you want to update. Ommited fields will not be
    updated. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored.

    __Minimum server version__: 9.5

    ##### Permissions
    Must have the `edit_bookmark_public_channel` or
    `edit_bookmark_private_channel` depending on the channel
    type. If the channel is a DM or GM, must be a non-guest
    member.

    Args:
        channel_id (str):
        bookmark_id (str):
        body (UpdateChannelBookmarkBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UpdateChannelBookmarkResponse]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        bookmark_id=bookmark_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str,
    bookmark_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateChannelBookmarkBody,
) -> Optional[Union[AppError, UpdateChannelBookmarkResponse]]:
    """Update channel bookmark

     Partially update a channel bookmark by providing only the
    fields you want to update. Ommited fields will not be
    updated. The fields that can be updated are defined in the
    request body, all other provided fields will be ignored.

    __Minimum server version__: 9.5

    ##### Permissions
    Must have the `edit_bookmark_public_channel` or
    `edit_bookmark_private_channel` depending on the channel
    type. If the channel is a DM or GM, must be a non-guest
    member.

    Args:
        channel_id (str):
        bookmark_id (str):
        body (UpdateChannelBookmarkBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UpdateChannelBookmarkResponse]
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            bookmark_id=bookmark_id,
            client=client,
            body=body,
        )
    ).parsed
