from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.channel import Channel
from ...models.patch_channel_body import PatchChannelBody
from ...types import Response


def _get_kwargs(
    channel_id: str,
    *,
    body: PatchChannelBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/channels/{channel_id}/patch",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, Channel]]:
    if response.status_code == 200:
        response_200 = Channel.from_dict(response.json())

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
) -> Response[Union[AppError, Channel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchChannelBody,
) -> Response[Union[AppError, Channel]]:
    """Patch a channel

     Partially update a channel by providing only the fields you want to update. Omitted fields will not
    be updated. The fields that can be updated are defined in the request body, all other provided
    fields will be ignored.
    ##### Permissions
    If updating a public channel, `manage_public_channel_members` permission is required. If updating a
    private channel, `manage_private_channel_members` permission is required.

    Args:
        channel_id (str):
        body (PatchChannelBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Channel]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchChannelBody,
) -> Optional[Union[AppError, Channel]]:
    """Patch a channel

     Partially update a channel by providing only the fields you want to update. Omitted fields will not
    be updated. The fields that can be updated are defined in the request body, all other provided
    fields will be ignored.
    ##### Permissions
    If updating a public channel, `manage_public_channel_members` permission is required. If updating a
    private channel, `manage_private_channel_members` permission is required.

    Args:
        channel_id (str):
        body (PatchChannelBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Channel]
    """

    return sync_detailed(
        channel_id=channel_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchChannelBody,
) -> Response[Union[AppError, Channel]]:
    """Patch a channel

     Partially update a channel by providing only the fields you want to update. Omitted fields will not
    be updated. The fields that can be updated are defined in the request body, all other provided
    fields will be ignored.
    ##### Permissions
    If updating a public channel, `manage_public_channel_members` permission is required. If updating a
    private channel, `manage_private_channel_members` permission is required.

    Args:
        channel_id (str):
        body (PatchChannelBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, Channel]]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: PatchChannelBody,
) -> Optional[Union[AppError, Channel]]:
    """Patch a channel

     Partially update a channel by providing only the fields you want to update. Omitted fields will not
    be updated. The fields that can be updated are defined in the request body, all other provided
    fields will be ignored.
    ##### Permissions
    If updating a public channel, `manage_public_channel_members` permission is required. If updating a
    private channel, `manage_private_channel_members` permission is required.

    Args:
        channel_id (str):
        body (PatchChannelBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, Channel]
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            client=client,
            body=body,
        )
    ).parsed
