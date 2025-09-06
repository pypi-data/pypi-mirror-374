import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ApiKeyResponse")


@_attrs_define
class ApiKeyResponse:
    """
    Attributes:
        id (str):
        key_name (str):
        key_prefix (str):
        is_active (bool):
        last_used_at (Union[None, datetime.datetime]):
        created_at (datetime.datetime):
        expires_at (Union[None, datetime.datetime]):
    """

    id: str
    key_name: str
    key_prefix: str
    is_active: bool
    last_used_at: Union[None, datetime.datetime]
    created_at: datetime.datetime
    expires_at: Union[None, datetime.datetime]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        key_name = self.key_name

        key_prefix = self.key_prefix

        is_active = self.is_active

        last_used_at: Union[None, str]
        if isinstance(self.last_used_at, datetime.datetime):
            last_used_at = self.last_used_at.isoformat()
        else:
            last_used_at = self.last_used_at

        created_at = self.created_at.isoformat()

        expires_at: Union[None, str]
        if isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "key_name": key_name,
                "key_prefix": key_prefix,
                "is_active": is_active,
                "last_used_at": last_used_at,
                "created_at": created_at,
                "expires_at": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        key_name = d.pop("key_name")

        key_prefix = d.pop("key_prefix")

        is_active = d.pop("is_active")

        def _parse_last_used_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_at_type_0 = isoparse(data)

                return last_used_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        last_used_at = _parse_last_used_at(d.pop("last_used_at"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_expires_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at"))

        api_key_response = cls(
            id=id,
            key_name=key_name,
            key_prefix=key_prefix,
            is_active=is_active,
            last_used_at=last_used_at,
            created_at=created_at,
            expires_at=expires_at,
        )

        api_key_response.additional_properties = d
        return api_key_response

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
