from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.delete_scheduled_post_response_200 import DeleteScheduledPostResponse200
from ...types import Response


def _get_kwargs(
    scheduled_post_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v4/posts/schedule/{scheduled_post_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, DeleteScheduledPostResponse200]]:
    if response.status_code == 200:
        response_200 = DeleteScheduledPostResponse200.from_dict(response.json())

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
) -> Response[Union[AppError, DeleteScheduledPostResponse200]]:
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
) -> Response[Union[AppError, DeleteScheduledPostResponse200]]:
    """Delete a scheduled post

     Delete a scheduled post
    __Minimum server version__: 10.3

    Args:
        scheduled_post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, DeleteScheduledPostResponse200]]
    """

    kwargs = _get_kwargs(
        scheduled_post_id=scheduled_post_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    scheduled_post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, DeleteScheduledPostResponse200]]:
    """Delete a scheduled post

     Delete a scheduled post
    __Minimum server version__: 10.3

    Args:
        scheduled_post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, DeleteScheduledPostResponse200]
    """

    return sync_detailed(
        scheduled_post_id=scheduled_post_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    scheduled_post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, DeleteScheduledPostResponse200]]:
    """Delete a scheduled post

     Delete a scheduled post
    __Minimum server version__: 10.3

    Args:
        scheduled_post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, DeleteScheduledPostResponse200]]
    """

    kwargs = _get_kwargs(
        scheduled_post_id=scheduled_post_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    scheduled_post_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, DeleteScheduledPostResponse200]]:
    """Delete a scheduled post

     Delete a scheduled post
    __Minimum server version__: 10.3

    Args:
        scheduled_post_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, DeleteScheduledPostResponse200]
    """

    return (
        await asyncio_detailed(
            scheduled_post_id=scheduled_post_id,
            client=client,
        )
    ).parsed
