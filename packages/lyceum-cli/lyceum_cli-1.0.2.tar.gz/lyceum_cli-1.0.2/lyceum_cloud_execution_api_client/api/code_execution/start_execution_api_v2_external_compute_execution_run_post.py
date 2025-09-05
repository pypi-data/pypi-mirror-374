from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.code_execution import CodeExecution
from ...models.http_validation_error import HTTPValidationError
from ...models.start_execution_api_v2_external_compute_execution_run_post_response_start_execution_api_v2_external_compute_execution_run_post import (
    StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost,
)
from ...types import Response


def _get_kwargs(
    *,
    body: CodeExecution,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/external/compute/execution/run",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        HTTPValidationError,
        StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost,
    ]
]:
    if response.status_code == 200:
        response_200 = StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost.from_dict(
            response.json()
        )

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        HTTPValidationError,
        StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CodeExecution,
) -> Response[
    Union[
        HTTPValidationError,
        StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost,
    ]
]:
    """Start Execution

     Start code execution and return execution_id immediately.

    Args:
        body (CodeExecution):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost]]
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
    client: Union[AuthenticatedClient, Client],
    body: CodeExecution,
) -> Optional[
    Union[
        HTTPValidationError,
        StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost,
    ]
]:
    """Start Execution

     Start code execution and return execution_id immediately.

    Args:
        body (CodeExecution):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CodeExecution,
) -> Response[
    Union[
        HTTPValidationError,
        StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost,
    ]
]:
    """Start Execution

     Start code execution and return execution_id immediately.

    Args:
        body (CodeExecution):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CodeExecution,
) -> Optional[
    Union[
        HTTPValidationError,
        StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost,
    ]
]:
    """Start Execution

     Start code execution and return execution_id immediately.

    Args:
        body (CodeExecution):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, StartExecutionApiV2ExternalComputeExecutionRunPostResponseStartExecutionApiV2ExternalComputeExecutionRunPost]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
