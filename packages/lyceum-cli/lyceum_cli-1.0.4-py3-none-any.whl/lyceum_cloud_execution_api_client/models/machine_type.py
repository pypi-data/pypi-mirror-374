from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MachineType")


@_attrs_define
class MachineType:
    """
    Attributes:
        hardware_profile (str):
        price_per_hour (float):
    """

    hardware_profile: str
    price_per_hour: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hardware_profile = self.hardware_profile

        price_per_hour = self.price_per_hour

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hardware_profile": hardware_profile,
                "price_per_hour": price_per_hour,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hardware_profile = d.pop("hardware_profile")

        price_per_hour = d.pop("price_per_hour")

        machine_type = cls(
            hardware_profile=hardware_profile,
            price_per_hour=price_per_hour,
        )

        machine_type.additional_properties = d
        return machine_type

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
