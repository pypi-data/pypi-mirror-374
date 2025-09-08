from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.file_info import FileInfo
from ...models.upload_data_body import UploadDataBody
from ...types import Response


def _get_kwargs(
    upload_id: str,
    *,
    body: UploadDataBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v4/uploads/{upload_id}",
    }

    _kwargs["data"] = body.to_dict()

    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, AppError, FileInfo]]:
    if response.status_code == 201:
        response_201 = FileInfo.from_dict(response.json())

        return response_201

    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

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
) -> Response[Union[Any, AppError, FileInfo]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    upload_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadDataBody,
) -> Response[Union[Any, AppError, FileInfo]]:
    """Perform a file upload

     Starts or resumes a file upload.
    To resume an existing (incomplete) upload, data should be sent starting from the offset specified in
    the upload session object.

    The request body can be in one of two formats:
    - Binary file content streamed in request's body
    - multipart/form-data

    ##### Permissions
    Must be logged in as the user who created the upload session.

    Args:
        upload_id (str):
        body (UploadDataBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError, FileInfo]]
    """

    kwargs = _get_kwargs(
        upload_id=upload_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    upload_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadDataBody,
) -> Optional[Union[Any, AppError, FileInfo]]:
    """Perform a file upload

     Starts or resumes a file upload.
    To resume an existing (incomplete) upload, data should be sent starting from the offset specified in
    the upload session object.

    The request body can be in one of two formats:
    - Binary file content streamed in request's body
    - multipart/form-data

    ##### Permissions
    Must be logged in as the user who created the upload session.

    Args:
        upload_id (str):
        body (UploadDataBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError, FileInfo]
    """

    return sync_detailed(
        upload_id=upload_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    upload_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadDataBody,
) -> Response[Union[Any, AppError, FileInfo]]:
    """Perform a file upload

     Starts or resumes a file upload.
    To resume an existing (incomplete) upload, data should be sent starting from the offset specified in
    the upload session object.

    The request body can be in one of two formats:
    - Binary file content streamed in request's body
    - multipart/form-data

    ##### Permissions
    Must be logged in as the user who created the upload session.

    Args:
        upload_id (str):
        body (UploadDataBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppError, FileInfo]]
    """

    kwargs = _get_kwargs(
        upload_id=upload_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    upload_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadDataBody,
) -> Optional[Union[Any, AppError, FileInfo]]:
    """Perform a file upload

     Starts or resumes a file upload.
    To resume an existing (incomplete) upload, data should be sent starting from the offset specified in
    the upload session object.

    The request body can be in one of two formats:
    - Binary file content streamed in request's body
    - multipart/form-data

    ##### Permissions
    Must be logged in as the user who created the upload session.

    Args:
        upload_id (str):
        body (UploadDataBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppError, FileInfo]
    """

    return (
        await asyncio_detailed(
            upload_id=upload_id,
            client=client,
            body=body,
        )
    ).parsed
