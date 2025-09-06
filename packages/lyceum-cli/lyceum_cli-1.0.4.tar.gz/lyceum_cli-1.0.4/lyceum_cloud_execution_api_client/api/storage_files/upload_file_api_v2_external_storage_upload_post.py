from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_upload_file_api_v2_external_storage_upload_post import BodyUploadFileApiV2ExternalStorageUploadPost
from ...models.http_validation_error import HTTPValidationError
from ...models.upload_response import UploadResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BodyUploadFileApiV2ExternalStorageUploadPost,
    key: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_key: Union[None, Unset, str]
    if isinstance(key, Unset):
        json_key = UNSET
    else:
        json_key = key
    params["key"] = json_key

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/external/storage/upload",
        "params": params,
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, UploadResponse]]:
    if response.status_code == 200:
        response_200 = UploadResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, UploadResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyUploadFileApiV2ExternalStorageUploadPost,
    key: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, UploadResponse]]:
    """Upload File

     Upload a file to user's S3 bucket.

    Args:
        key (Union[None, Unset, str]):
        body (BodyUploadFileApiV2ExternalStorageUploadPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, UploadResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        key=key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyUploadFileApiV2ExternalStorageUploadPost,
    key: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, UploadResponse]]:
    """Upload File

     Upload a file to user's S3 bucket.

    Args:
        key (Union[None, Unset, str]):
        body (BodyUploadFileApiV2ExternalStorageUploadPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, UploadResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
        key=key,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyUploadFileApiV2ExternalStorageUploadPost,
    key: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, UploadResponse]]:
    """Upload File

     Upload a file to user's S3 bucket.

    Args:
        key (Union[None, Unset, str]):
        body (BodyUploadFileApiV2ExternalStorageUploadPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, UploadResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        key=key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyUploadFileApiV2ExternalStorageUploadPost,
    key: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, UploadResponse]]:
    """Upload File

     Upload a file to user's S3 bucket.

    Args:
        key (Union[None, Unset, str]):
        body (BodyUploadFileApiV2ExternalStorageUploadPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, UploadResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            key=key,
        )
    ).parsed
