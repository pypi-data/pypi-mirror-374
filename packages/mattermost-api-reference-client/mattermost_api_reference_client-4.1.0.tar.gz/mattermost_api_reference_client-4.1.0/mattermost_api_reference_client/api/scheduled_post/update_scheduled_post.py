from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.update_scheduled_post_body import UpdateScheduledPostBody
from ...models.update_scheduled_post_response_200 import UpdateScheduledPostResponse200
from ...types import Response


def _get_kwargs(
    scheduled_post_id: str,
    *,
    body: UpdateScheduledPostBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v4/posts/schedule/{scheduled_post_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, UpdateScheduledPostResponse200]]:
    if response.status_code == 200:
        response_200 = UpdateScheduledPostResponse200.from_dict(response.json())

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

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, UpdateScheduledPostResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    scheduled_post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateScheduledPostBody,
) -> Response[Union[AppError, UpdateScheduledPostResponse200]]:
    """Update a scheduled post

     Updates a scheduled post
    ##### Permissions
    Must have `create_post` permission for the channel where the scheduled post belongs to.
    __Minimum server version__: 10.3

    Args:
        scheduled_post_id (str):
        body (UpdateScheduledPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UpdateScheduledPostResponse200]]
    """

    kwargs = _get_kwargs(
        scheduled_post_id=scheduled_post_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scheduled_post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateScheduledPostBody,
) -> Optional[Union[AppError, UpdateScheduledPostResponse200]]:
    """Update a scheduled post

     Updates a scheduled post
    ##### Permissions
    Must have `create_post` permission for the channel where the scheduled post belongs to.
    __Minimum server version__: 10.3

    Args:
        scheduled_post_id (str):
        body (UpdateScheduledPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UpdateScheduledPostResponse200]
    """

    return sync_detailed(
        scheduled_post_id=scheduled_post_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    scheduled_post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateScheduledPostBody,
) -> Response[Union[AppError, UpdateScheduledPostResponse200]]:
    """Update a scheduled post

     Updates a scheduled post
    ##### Permissions
    Must have `create_post` permission for the channel where the scheduled post belongs to.
    __Minimum server version__: 10.3

    Args:
        scheduled_post_id (str):
        body (UpdateScheduledPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UpdateScheduledPostResponse200]]
    """

    kwargs = _get_kwargs(
        scheduled_post_id=scheduled_post_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scheduled_post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateScheduledPostBody,
) -> Optional[Union[AppError, UpdateScheduledPostResponse200]]:
    """Update a scheduled post

     Updates a scheduled post
    ##### Permissions
    Must have `create_post` permission for the channel where the scheduled post belongs to.
    __Minimum server version__: 10.3

    Args:
        scheduled_post_id (str):
        body (UpdateScheduledPostBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UpdateScheduledPostResponse200]
    """

    return (
        await asyncio_detailed(
            scheduled_post_id=scheduled_post_id,
            client=client,
            body=body,
        )
    ).parsed
