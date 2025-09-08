from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...types import Response


def _get_kwargs(
    import_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v4/imports/{import_name}",
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
    import_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AppError]:
    """Delete an import file

     Deletes an import file.


    __Minimum server version__: 5.31

    ##### Permissions

    Must have `manage_system` permissions.

    Args:
        import_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs(
        import_name=import_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    import_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AppError]:
    """Delete an import file

     Deletes an import file.


    __Minimum server version__: 5.31

    ##### Permissions

    Must have `manage_system` permissions.

    Args:
        import_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return sync_detailed(
        import_name=import_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    import_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AppError]:
    """Delete an import file

     Deletes an import file.


    __Minimum server version__: 5.31

    ##### Permissions

    Must have `manage_system` permissions.

    Args:
        import_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AppError]
    """

    kwargs = _get_kwargs(
        import_name=import_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    import_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AppError]:
    """Delete an import file

     Deletes an import file.


    __Minimum server version__: 5.31

    ##### Permissions

    Must have `manage_system` permissions.

    Args:
        import_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AppError
    """

    return (
        await asyncio_detailed(
            import_name=import_name,
            client=client,
        )
    ).parsed
