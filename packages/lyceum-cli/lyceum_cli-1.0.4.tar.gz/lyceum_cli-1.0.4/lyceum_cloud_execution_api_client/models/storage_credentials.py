import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="StorageCredentials")


@_attrs_define
class StorageCredentials:
    """
    Attributes:
        access_key (str):
        secret_key (str):
        endpoint (str):
        bucket_name (str):
        expires_at (datetime.datetime):
        session_token (Union[Unset, str]):
        region (Union[Unset, str]):  Default: 'us-east-1'.
    """

    access_key: str
    secret_key: str
    endpoint: str
    bucket_name: str
    expires_at: datetime.datetime
    session_token: Union[Unset, str] = UNSET
    region: Union[Unset, str] = "us-east-1"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_key = self.access_key

        secret_key = self.secret_key

        endpoint = self.endpoint

        bucket_name = self.bucket_name

        expires_at = self.expires_at.isoformat()

        session_token = self.session_token

        region = self.region

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_key": access_key,
                "secret_key": secret_key,
                "endpoint": endpoint,
                "bucket_name": bucket_name,
                "expires_at": expires_at,
            }
        )
        if session_token is not UNSET:
            field_dict["session_token"] = session_token
        if region is not UNSET:
            field_dict["region"] = region

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_key = d.pop("access_key")

        secret_key = d.pop("secret_key")

        endpoint = d.pop("endpoint")

        bucket_name = d.pop("bucket_name")

        expires_at = isoparse(d.pop("expires_at"))

        session_token = d.pop("session_token", UNSET)

        region = d.pop("region", UNSET)

        storage_credentials = cls(
            access_key=access_key,
            secret_key=secret_key,
            endpoint=endpoint,
            bucket_name=bucket_name,
            expires_at=expires_at,
            session_token=session_token,
            region=region,
        )

        storage_credentials.additional_properties = d
        return storage_credentials

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
