from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...types import Response


def _get_kwargs(
    export_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/exports/{export_name}",
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

    if response.status_code == 404:
        response_404 = AppError.from_dict(response.json())

        return response_404

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

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
    export_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AppError]:
    """Download an export file

     Downloads an export file.


    __Minimum server version__: 5.33

    ##### Permissions

    Must have `manage_system` permissions.

    Args:
        export_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs(
        export_name=export_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    export_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AppError]:
    """Download an export file

     Downloads an export file.


    __Minimum server version__: 5.33

    ##### Permissions

    Must have `manage_system` permissions.

    Args:
        export_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return sync_detailed(
        export_name=export_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    export_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AppError]:
    """Download an export file

     Downloads an export file.


    __Minimum server version__: 5.33

    ##### Permissions

    Must have `manage_system` permissions.

    Args:
        export_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs(
        export_name=export_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    export_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AppError]:
    """Download an export file

     Downloads an export file.


    __Minimum server version__: 5.33

    ##### Permissions

    Must have `manage_system` permissions.

    Args:
        export_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return (
        await asyncio_detailed(
            export_name=export_name,
            client=client,
        )
    ).parsed
