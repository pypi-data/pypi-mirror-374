from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.preview_modal_content_data import PreviewModalContentData
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/cloud/preview/modal_data",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, list["PreviewModalContentData"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PreviewModalContentData.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

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


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, list["PreviewModalContentData"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, list["PreviewModalContentData"]]]:
    """Get cloud preview modal data

     Retrieves modal content data from the configured S3 bucket for displaying cloud product preview
    modals.
    ##### Permissions
    Must be authenticated. Must be in a Cloud Preview environment.
    __Minimum server version__: 10.0 __Note:__ This is intended for internal use and is subject to
    change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['PreviewModalContentData']]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, list["PreviewModalContentData"]]]:
    """Get cloud preview modal data

     Retrieves modal content data from the configured S3 bucket for displaying cloud product preview
    modals.
    ##### Permissions
    Must be authenticated. Must be in a Cloud Preview environment.
    __Minimum server version__: 10.0 __Note:__ This is intended for internal use and is subject to
    change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['PreviewModalContentData']]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, list["PreviewModalContentData"]]]:
    """Get cloud preview modal data

     Retrieves modal content data from the configured S3 bucket for displaying cloud product preview
    modals.
    ##### Permissions
    Must be authenticated. Must be in a Cloud Preview environment.
    __Minimum server version__: 10.0 __Note:__ This is intended for internal use and is subject to
    change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, list['PreviewModalContentData']]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, list["PreviewModalContentData"]]]:
    """Get cloud preview modal data

     Retrieves modal content data from the configured S3 bucket for displaying cloud product preview
    modals.
    ##### Permissions
    Must be authenticated. Must be in a Cloud Preview environment.
    __Minimum server version__: 10.0 __Note:__ This is intended for internal use and is subject to
    change.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, list['PreviewModalContentData']]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
