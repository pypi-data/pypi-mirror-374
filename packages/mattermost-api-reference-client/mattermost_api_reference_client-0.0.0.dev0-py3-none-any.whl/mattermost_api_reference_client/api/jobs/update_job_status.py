from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.status_ok import StatusOK
from ...models.update_job_status_body import UpdateJobStatusBody
from ...types import Response


def _get_kwargs(
    job_id: str,
    *,
    body: UpdateJobStatusBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/api/v4/jobs/{job_id}/status",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, StatusOK]]:
    if response.status_code == 200:
        response_200 = StatusOK.from_dict(response.json())

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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, StatusOK]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateJobStatusBody,
) -> Response[Union[AppError, StatusOK]]:
    """Update the status of a job

     Update the status of a job. Valid status updates: - 'in_progress' -> 'pending' - 'in_progress' |
    'pending' -> 'cancel_requested' - 'cancel_requested' -> 'canceled'
    Add force to the body of the PATCH request to bypass the given rules, the only statuses you can go
    to are: pending, cancel_requested and canceled. This can have unexpected consequences and should be
    used with caution.

    Args:
        job_id (str):
        body (UpdateJobStatusBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateJobStatusBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Update the status of a job

     Update the status of a job. Valid status updates: - 'in_progress' -> 'pending' - 'in_progress' |
    'pending' -> 'cancel_requested' - 'cancel_requested' -> 'canceled'
    Add force to the body of the PATCH request to bypass the given rules, the only statuses you can go
    to are: pending, cancel_requested and canceled. This can have unexpected consequences and should be
    used with caution.

    Args:
        job_id (str):
        body (UpdateJobStatusBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateJobStatusBody,
) -> Response[Union[AppError, StatusOK]]:
    """Update the status of a job

     Update the status of a job. Valid status updates: - 'in_progress' -> 'pending' - 'in_progress' |
    'pending' -> 'cancel_requested' - 'cancel_requested' -> 'canceled'
    Add force to the body of the PATCH request to bypass the given rules, the only statuses you can go
    to are: pending, cancel_requested and canceled. This can have unexpected consequences and should be
    used with caution.

    Args:
        job_id (str):
        body (UpdateJobStatusBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, StatusOK]]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateJobStatusBody,
) -> Optional[Union[AppError, StatusOK]]:
    """Update the status of a job

     Update the status of a job. Valid status updates: - 'in_progress' -> 'pending' - 'in_progress' |
    'pending' -> 'cancel_requested' - 'cancel_requested' -> 'canceled'
    Add force to the body of the PATCH request to bypass the given rules, the only statuses you can go
    to are: pending, cancel_requested and canceled. This can have unexpected consequences and should be
    used with caution.

    Args:
        job_id (str):
        body (UpdateJobStatusBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, StatusOK]
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
            body=body,
        )
    ).parsed
