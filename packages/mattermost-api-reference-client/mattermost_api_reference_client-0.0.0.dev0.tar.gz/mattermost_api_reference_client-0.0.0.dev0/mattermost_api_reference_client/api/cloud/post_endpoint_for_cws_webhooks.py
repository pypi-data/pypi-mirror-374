from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/cloud/webhook",
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[AppError]:
    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[AppError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AppError]:
    """POST endpoint for CWS Webhooks

     An endpoint for processing webhooks from the Customer Portal
    ##### Permissions
    This endpoint should only be accessed by CWS, in a Mattermost Cloud instance
    __Minimum server version__: 5.30 __Note:__ This is intended for internal use and is subject to
    change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AppError]:
    """POST endpoint for CWS Webhooks

     An endpoint for processing webhooks from the Customer Portal
    ##### Permissions
    This endpoint should only be accessed by CWS, in a Mattermost Cloud instance
    __Minimum server version__: 5.30 __Note:__ This is intended for internal use and is subject to
    change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AppError]:
    """POST endpoint for CWS Webhooks

     An endpoint for processing webhooks from the Customer Portal
    ##### Permissions
    This endpoint should only be accessed by CWS, in a Mattermost Cloud instance
    __Minimum server version__: 5.30 __Note:__ This is intended for internal use and is subject to
    change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AppError]:
    """POST endpoint for CWS Webhooks

     An endpoint for processing webhooks from the Customer Portal
    ##### Permissions
    This endpoint should only be accessed by CWS, in a Mattermost Cloud instance
    __Minimum server version__: 5.30 __Note:__ This is intended for internal use and is subject to
    change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
