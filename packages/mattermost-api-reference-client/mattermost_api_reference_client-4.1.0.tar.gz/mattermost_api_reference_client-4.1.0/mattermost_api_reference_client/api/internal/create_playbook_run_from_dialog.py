from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_playbook_run_from_dialog_body import CreatePlaybookRunFromDialogBody
from ...models.error import Error
from ...models.playbook_run import PlaybookRun
from ...types import Response


def _get_kwargs(
    *,
    body: CreatePlaybookRunFromDialogBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/plugins/playbooks/api/v0/runs/dialog",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, PlaybookRun]]:
    if response.status_code == 201:
        response_201 = PlaybookRun.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, PlaybookRun]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CreatePlaybookRunFromDialogBody,
) -> Response[Union[Error, PlaybookRun]]:
    """Create a new playbook run from dialog

     This is an internal endpoint to create a playbook run from the submission of an interactive dialog,
    filled by a user in the webapp. See [Interactive
    Dialogs](https://docs.mattermost.com/developer/interactive-dialogs.html) for more information.

    Args:
        body (CreatePlaybookRunFromDialogBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, PlaybookRun]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: CreatePlaybookRunFromDialogBody,
) -> Optional[Union[Error, PlaybookRun]]:
    """Create a new playbook run from dialog

     This is an internal endpoint to create a playbook run from the submission of an interactive dialog,
    filled by a user in the webapp. See [Interactive
    Dialogs](https://docs.mattermost.com/developer/interactive-dialogs.html) for more information.

    Args:
        body (CreatePlaybookRunFromDialogBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, PlaybookRun]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CreatePlaybookRunFromDialogBody,
) -> Response[Union[Error, PlaybookRun]]:
    """Create a new playbook run from dialog

     This is an internal endpoint to create a playbook run from the submission of an interactive dialog,
    filled by a user in the webapp. See [Interactive
    Dialogs](https://docs.mattermost.com/developer/interactive-dialogs.html) for more information.

    Args:
        body (CreatePlaybookRunFromDialogBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, PlaybookRun]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CreatePlaybookRunFromDialogBody,
) -> Optional[Union[Error, PlaybookRun]]:
    """Create a new playbook run from dialog

     This is an internal endpoint to create a playbook run from the submission of an interactive dialog,
    filled by a user in the webapp. See [Interactive
    Dialogs](https://docs.mattermost.com/developer/interactive-dialogs.html) for more information.

    Args:
        body (CreatePlaybookRunFromDialogBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, PlaybookRun]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
