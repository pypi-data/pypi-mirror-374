from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.integrity_check_result import IntegrityCheckResult
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v4/integrity",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["IntegrityCheckResult"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = IntegrityCheckResult.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["IntegrityCheckResult"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[list["IntegrityCheckResult"]]:
    """Perform a database integrity check

     Performs a database integrity check.


    __Note__: This check may temporarily harm system performance.


    __Minimum server version__: 5.28.0


    __Local mode only__: This endpoint is only available through [local
    mode](https://docs.mattermost.com/administration/mmctl-cli-tool.html#local-mode).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['IntegrityCheckResult']]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[list["IntegrityCheckResult"]]:
    """Perform a database integrity check

     Performs a database integrity check.


    __Note__: This check may temporarily harm system performance.


    __Minimum server version__: 5.28.0


    __Local mode only__: This endpoint is only available through [local
    mode](https://docs.mattermost.com/administration/mmctl-cli-tool.html#local-mode).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['IntegrityCheckResult']
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[list["IntegrityCheckResult"]]:
    """Perform a database integrity check

     Performs a database integrity check.


    __Note__: This check may temporarily harm system performance.


    __Minimum server version__: 5.28.0


    __Local mode only__: This endpoint is only available through [local
    mode](https://docs.mattermost.com/administration/mmctl-cli-tool.html#local-mode).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['IntegrityCheckResult']]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[list["IntegrityCheckResult"]]:
    """Perform a database integrity check

     Performs a database integrity check.


    __Note__: This check may temporarily harm system performance.


    __Minimum server version__: 5.28.0


    __Local mode only__: This endpoint is only available through [local
    mode](https://docs.mattermost.com/administration/mmctl-cli-tool.html#local-mode).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['IntegrityCheckResult']
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
