from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.connect_request_credentials import ConnectRequestCredentials


T = TypeVar("T", bound="ConnectRequest")


@_attrs_define
class ConnectRequest:
    """
    Attributes:
        provider (str):
        credentials (ConnectRequestCredentials):
    """

    provider: str
    credentials: "ConnectRequestCredentials"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        credentials = self.credentials.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
                "credentials": credentials,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connect_request_credentials import ConnectRequestCredentials

        d = dict(src_dict)
        provider = d.pop("provider")

        credentials = ConnectRequestCredentials.from_dict(d.pop("credentials"))

        connect_request = cls(
            provider=provider,
            credentials=credentials,
        )

        connect_request.additional_properties = d
        return connect_request

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
