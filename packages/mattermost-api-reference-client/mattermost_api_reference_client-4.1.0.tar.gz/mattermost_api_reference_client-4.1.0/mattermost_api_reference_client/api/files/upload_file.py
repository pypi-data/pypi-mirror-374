from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.upload_file_body import UploadFileBody
from ...models.upload_file_response_201 import UploadFileResponse201
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: UploadFileBody,
    channel_id: Union[Unset, str] = UNSET,
    filename: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["channel_id"] = channel_id

    params["filename"] = filename

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/files",
        "params": params,
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, UploadFileResponse201]]:
    if response.status_code == 201:
        response_201 = UploadFileResponse201.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = AppError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 413:
        response_413 = AppError.from_dict(response.json())

        return response_413

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, UploadFileResponse201]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadFileBody,
    channel_id: Union[Unset, str] = UNSET,
    filename: Union[Unset, str] = UNSET,
) -> Response[Union[AppError, UploadFileResponse201]]:
    """Upload a file

     Uploads a file that can later be attached to a post.

    This request can either be a multipart/form-data request with a channel_id, files and optional
    client_ids defined in the FormData, or it can be a request with the channel_id and filename
    defined as query parameters with the contents of a single file in the body of the request.

    Only multipart/form-data requests are supported by server versions up to and including 4.7.
    Server versions 4.8 and higher support both types of requests.

    __Minimum server version__: 9.4
    Starting with server version 9.4 when uploading a file for a channel bookmark, the bookmark=true
    query parameter should be included in the query string

    ##### Permissions
    Must have `upload_file` permission.

    Args:
        channel_id (Union[Unset, str]):
        filename (Union[Unset, str]):
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UploadFileResponse201]]
    """

    kwargs = _get_kwargs(
        body=body,
        channel_id=channel_id,
        filename=filename,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadFileBody,
    channel_id: Union[Unset, str] = UNSET,
    filename: Union[Unset, str] = UNSET,
) -> Optional[Union[AppError, UploadFileResponse201]]:
    """Upload a file

     Uploads a file that can later be attached to a post.

    This request can either be a multipart/form-data request with a channel_id, files and optional
    client_ids defined in the FormData, or it can be a request with the channel_id and filename
    defined as query parameters with the contents of a single file in the body of the request.

    Only multipart/form-data requests are supported by server versions up to and including 4.7.
    Server versions 4.8 and higher support both types of requests.

    __Minimum server version__: 9.4
    Starting with server version 9.4 when uploading a file for a channel bookmark, the bookmark=true
    query parameter should be included in the query string

    ##### Permissions
    Must have `upload_file` permission.

    Args:
        channel_id (Union[Unset, str]):
        filename (Union[Unset, str]):
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UploadFileResponse201]
    """

    return sync_detailed(
        client=client,
        body=body,
        channel_id=channel_id,
        filename=filename,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadFileBody,
    channel_id: Union[Unset, str] = UNSET,
    filename: Union[Unset, str] = UNSET,
) -> Response[Union[AppError, UploadFileResponse201]]:
    """Upload a file

     Uploads a file that can later be attached to a post.

    This request can either be a multipart/form-data request with a channel_id, files and optional
    client_ids defined in the FormData, or it can be a request with the channel_id and filename
    defined as query parameters with the contents of a single file in the body of the request.

    Only multipart/form-data requests are supported by server versions up to and including 4.7.
    Server versions 4.8 and higher support both types of requests.

    __Minimum server version__: 9.4
    Starting with server version 9.4 when uploading a file for a channel bookmark, the bookmark=true
    query parameter should be included in the query string

    ##### Permissions
    Must have `upload_file` permission.

    Args:
        channel_id (Union[Unset, str]):
        filename (Union[Unset, str]):
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, UploadFileResponse201]]
    """

    kwargs = _get_kwargs(
        body=body,
        channel_id=channel_id,
        filename=filename,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadFileBody,
    channel_id: Union[Unset, str] = UNSET,
    filename: Union[Unset, str] = UNSET,
) -> Optional[Union[AppError, UploadFileResponse201]]:
    """Upload a file

     Uploads a file that can later be attached to a post.

    This request can either be a multipart/form-data request with a channel_id, files and optional
    client_ids defined in the FormData, or it can be a request with the channel_id and filename
    defined as query parameters with the contents of a single file in the body of the request.

    Only multipart/form-data requests are supported by server versions up to and including 4.7.
    Server versions 4.8 and higher support both types of requests.

    __Minimum server version__: 9.4
    Starting with server version 9.4 when uploading a file for a channel bookmark, the bookmark=true
    query parameter should be included in the query string

    ##### Permissions
    Must have `upload_file` permission.

    Args:
        channel_id (Union[Unset, str]):
        filename (Union[Unset, str]):
        body (UploadFileBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, UploadFileResponse201]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            channel_id=channel_id,
            filename=filename,
        )
    ).parsed
