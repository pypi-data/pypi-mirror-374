from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.data_retention_policy_with_team_and_channel_counts import DataRetentionPolicyWithTeamAndChannelCounts
from ...types import Response


def _get_kwargs(
    policy_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v4/data_retention/policies/{policy_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]]:
    if response.status_code == 200:
        response_200 = DataRetentionPolicyWithTeamAndChannelCounts.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = AppError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AppError.from_dict(response.json())

        return response_403

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if response.status_code == 501:
        response_501 = AppError.from_dict(response.json())

        return response_501

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]]:
    """Get a granular data retention policy

     Gets details about a granular data retention policies by ID.

    __Minimum server version__: 5.35

    ##### Permissions
    Must have the `sysconsole_read_compliance_data_retention` permission.

    ##### License
    Requires an E20 license.

    Args:
        policy_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]]
    """

    kwargs = _get_kwargs(
        policy_id=policy_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]]:
    """Get a granular data retention policy

     Gets details about a granular data retention policies by ID.

    __Minimum server version__: 5.35

    ##### Permissions
    Must have the `sysconsole_read_compliance_data_retention` permission.

    ##### License
    Requires an E20 license.

    Args:
        policy_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]
    """

    return sync_detailed(
        policy_id=policy_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]]:
    """Get a granular data retention policy

     Gets details about a granular data retention policies by ID.

    __Minimum server version__: 5.35

    ##### Permissions
    Must have the `sysconsole_read_compliance_data_retention` permission.

    ##### License
    Requires an E20 license.

    Args:
        policy_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]]
    """

    kwargs = _get_kwargs(
        policy_id=policy_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]]:
    """Get a granular data retention policy

     Gets details about a granular data retention policies by ID.

    __Minimum server version__: 5.35

    ##### Permissions
    Must have the `sysconsole_read_compliance_data_retention` permission.

    ##### License
    Requires an E20 license.

    Args:
        policy_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, DataRetentionPolicyWithTeamAndChannelCounts]
    """

    return (
        await asyncio_detailed(
            policy_id=policy_id,
            client=client,
        )
    ).parsed
