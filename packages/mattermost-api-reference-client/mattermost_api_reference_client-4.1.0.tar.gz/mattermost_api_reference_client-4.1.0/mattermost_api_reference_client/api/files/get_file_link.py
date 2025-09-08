from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.get_file_link_response_200 import GetFileLinkResponse200
from ...types import Response


def _get_kwargs(
    file_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/files/{file_id}/link",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, GetFileLinkResponse200]]:
    if response.status_code == 200:
        response_200 = GetFileLinkResponse200.from_dict(response.json())

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

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, GetFileLinkResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    file_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GetFileLinkResponse200]]:
    """Get a public file link

     Gets a public link for a file that can be accessed without logging into Mattermost.
    ##### Permissions
    Must have `read_channel` permission or be uploader of the file.

    Args:
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetFileLinkResponse200]]
    """

    kwargs = _get_kwargs(
        file_id=file_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    file_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GetFileLinkResponse200]]:
    """Get a public file link

     Gets a public link for a file that can be accessed without logging into Mattermost.
    ##### Permissions
    Must have `read_channel` permission or be uploader of the file.

    Args:
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetFileLinkResponse200]
    """

    return sync_detailed(
        file_id=file_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    file_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, GetFileLinkResponse200]]:
    """Get a public file link

     Gets a public link for a file that can be accessed without logging into Mattermost.
    ##### Permissions
    Must have `read_channel` permission or be uploader of the file.

    Args:
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, GetFileLinkResponse200]]
    """

    kwargs = _get_kwargs(
        file_id=file_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    file_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, GetFileLinkResponse200]]:
    """Get a public file link

     Gets a public link for a file that can be accessed without logging into Mattermost.
    ##### Permissions
    Must have `read_channel` permission or be uploader of the file.

    Args:
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, GetFileLinkResponse200]
    """

    return (
        await asyncio_detailed(
            file_id=file_id,
            client=client,
        )
    ).parsed
