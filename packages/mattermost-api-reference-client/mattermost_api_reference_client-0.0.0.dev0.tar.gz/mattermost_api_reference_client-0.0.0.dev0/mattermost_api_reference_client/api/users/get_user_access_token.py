from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.user_access_token_sanitized import UserAccessTokenSanitized
from ...types import Response


def _get_kwargs(
    token_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/users/tokens/{token_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, UserAccessTokenSanitized]]:
    if response.status_code == 200:
        response_200 = UserAccessTokenSanitized.from_dict(response.json())

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
) -> Response[Union[AppError, UserAccessTokenSanitized]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    token_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, UserAccessTokenSanitized]]:
    """Get a user access token

     Get a user access token. Does not include the actual authentication token.

    __Minimum server version__: 4.1

    ##### Permissions
    Must have `read_user_access_token` permission. For non-self requests, must also have the
    `edit_other_users` permission.

    Args:
        token_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UserAccessTokenSanitized]]
    """

    kwargs = _get_kwargs(
        token_id=token_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    token_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, UserAccessTokenSanitized]]:
    """Get a user access token

     Get a user access token. Does not include the actual authentication token.

    __Minimum server version__: 4.1

    ##### Permissions
    Must have `read_user_access_token` permission. For non-self requests, must also have the
    `edit_other_users` permission.

    Args:
        token_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UserAccessTokenSanitized]
    """

    return sync_detailed(
        token_id=token_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    token_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, UserAccessTokenSanitized]]:
    """Get a user access token

     Get a user access token. Does not include the actual authentication token.

    __Minimum server version__: 4.1

    ##### Permissions
    Must have `read_user_access_token` permission. For non-self requests, must also have the
    `edit_other_users` permission.

    Args:
        token_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UserAccessTokenSanitized]]
    """

    kwargs = _get_kwargs(
        token_id=token_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    token_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, UserAccessTokenSanitized]]:
    """Get a user access token

     Get a user access token. Does not include the actual authentication token.

    __Minimum server version__: 4.1

    ##### Permissions
    Must have `read_user_access_token` permission. For non-self requests, must also have the
    `edit_other_users` permission.

    Args:
        token_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UserAccessTokenSanitized]
    """

    return (
        await asyncio_detailed(
            token_id=token_id,
            client=client,
        )
    ).parsed
