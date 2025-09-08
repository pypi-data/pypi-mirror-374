from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.app_error import AppError
from ...models.system_status_response import SystemStatusResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    get_server_status: Union[Unset, bool] = UNSET,
    device_id: Union[Unset, str] = UNSET,
    use_rest_semantics: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["get_server_status"] = get_server_status

    params["device_id"] = device_id

    params["use_rest_semantics"] = use_rest_semantics

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v4/system/ping",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AppError, SystemStatusResponse]]:
    if response.status_code == 200:
        response_200 = SystemStatusResponse.from_dict(response.json())

        return response_200

    if response.status_code == 500:
        response_500 = AppError.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AppError, SystemStatusResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    get_server_status: Union[Unset, bool] = UNSET,
    device_id: Union[Unset, str] = UNSET,
    use_rest_semantics: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, SystemStatusResponse]]:
    r"""Check system health

     Check if the server is up and healthy based on the configuration setting `GoRoutineHealthThreshold`.
    If `GoRoutineHealthThreshold` and the number of goroutines on the server exceeds that threshold the
    server is considered unhealthy. If `GoRoutineHealthThreshold` is not set or the number of goroutines
    is below the threshold the server is considered healthy.
    __Minimum server version__: 3.10
    If a \"device_id\" is passed in the query, it will test the Push Notification Proxy in order to
    discover whether the device is able to receive notifications. The response will have a
    \"CanReceiveNotifications\" property with one of the following values: - true: It can receive
    notifications - false: It cannot receive notifications - unknown: There has been an unknown error,
    and it is not certain whether it can

      receive notifications.

    __Minimum server version__: 6.5
    If \"use_rest_semantics\" is set to true in the query, the endpoint will not return an error status
    code in the header if the request is somehow completed successfully.
    __Minimum server version__: 9.6
    ##### Permissions
    None.

    Args:
        get_server_status (Union[Unset, bool]):
        device_id (Union[Unset, str]):
        use_rest_semantics (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SystemStatusResponse]]
    """

    kwargs = _get_kwargs(
        get_server_status=get_server_status,
        device_id=device_id,
        use_rest_semantics=use_rest_semantics,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    get_server_status: Union[Unset, bool] = UNSET,
    device_id: Union[Unset, str] = UNSET,
    use_rest_semantics: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, SystemStatusResponse]]:
    r"""Check system health

     Check if the server is up and healthy based on the configuration setting `GoRoutineHealthThreshold`.
    If `GoRoutineHealthThreshold` and the number of goroutines on the server exceeds that threshold the
    server is considered unhealthy. If `GoRoutineHealthThreshold` is not set or the number of goroutines
    is below the threshold the server is considered healthy.
    __Minimum server version__: 3.10
    If a \"device_id\" is passed in the query, it will test the Push Notification Proxy in order to
    discover whether the device is able to receive notifications. The response will have a
    \"CanReceiveNotifications\" property with one of the following values: - true: It can receive
    notifications - false: It cannot receive notifications - unknown: There has been an unknown error,
    and it is not certain whether it can

      receive notifications.

    __Minimum server version__: 6.5
    If \"use_rest_semantics\" is set to true in the query, the endpoint will not return an error status
    code in the header if the request is somehow completed successfully.
    __Minimum server version__: 9.6
    ##### Permissions
    None.

    Args:
        get_server_status (Union[Unset, bool]):
        device_id (Union[Unset, str]):
        use_rest_semantics (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SystemStatusResponse]
    """

    return sync_detailed(
        client=client,
        get_server_status=get_server_status,
        device_id=device_id,
        use_rest_semantics=use_rest_semantics,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    get_server_status: Union[Unset, bool] = UNSET,
    device_id: Union[Unset, str] = UNSET,
    use_rest_semantics: Union[Unset, bool] = UNSET,
) -> Response[Union[AppError, SystemStatusResponse]]:
    r"""Check system health

     Check if the server is up and healthy based on the configuration setting `GoRoutineHealthThreshold`.
    If `GoRoutineHealthThreshold` and the number of goroutines on the server exceeds that threshold the
    server is considered unhealthy. If `GoRoutineHealthThreshold` is not set or the number of goroutines
    is below the threshold the server is considered healthy.
    __Minimum server version__: 3.10
    If a \"device_id\" is passed in the query, it will test the Push Notification Proxy in order to
    discover whether the device is able to receive notifications. The response will have a
    \"CanReceiveNotifications\" property with one of the following values: - true: It can receive
    notifications - false: It cannot receive notifications - unknown: There has been an unknown error,
    and it is not certain whether it can

      receive notifications.

    __Minimum server version__: 6.5
    If \"use_rest_semantics\" is set to true in the query, the endpoint will not return an error status
    code in the header if the request is somehow completed successfully.
    __Minimum server version__: 9.6
    ##### Permissions
    None.

    Args:
        get_server_status (Union[Unset, bool]):
        device_id (Union[Unset, str]):
        use_rest_semantics (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AppError, SystemStatusResponse]]
    """

    kwargs = _get_kwargs(
        get_server_status=get_server_status,
        device_id=device_id,
        use_rest_semantics=use_rest_semantics,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    get_server_status: Union[Unset, bool] = UNSET,
    device_id: Union[Unset, str] = UNSET,
    use_rest_semantics: Union[Unset, bool] = UNSET,
) -> Optional[Union[AppError, SystemStatusResponse]]:
    r"""Check system health

     Check if the server is up and healthy based on the configuration setting `GoRoutineHealthThreshold`.
    If `GoRoutineHealthThreshold` and the number of goroutines on the server exceeds that threshold the
    server is considered unhealthy. If `GoRoutineHealthThreshold` is not set or the number of goroutines
    is below the threshold the server is considered healthy.
    __Minimum server version__: 3.10
    If a \"device_id\" is passed in the query, it will test the Push Notification Proxy in order to
    discover whether the device is able to receive notifications. The response will have a
    \"CanReceiveNotifications\" property with one of the following values: - true: It can receive
    notifications - false: It cannot receive notifications - unknown: There has been an unknown error,
    and it is not certain whether it can

      receive notifications.

    __Minimum server version__: 6.5
    If \"use_rest_semantics\" is set to true in the query, the endpoint will not return an error status
    code in the header if the request is somehow completed successfully.
    __Minimum server version__: 9.6
    ##### Permissions
    None.

    Args:
        get_server_status (Union[Unset, bool]):
        device_id (Union[Unset, str]):
        use_rest_semantics (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AppError, SystemStatusResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            get_server_status=get_server_status,
            device_id=device_id,
            use_rest_semantics=use_rest_semantics,
        )
    ).parsed
