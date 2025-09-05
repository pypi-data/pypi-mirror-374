from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.machine_type import MachineType


T = TypeVar("T", bound="MachineTypesResponse")


@_attrs_define
class MachineTypesResponse:
    """
    Attributes:
        machine_types (list['MachineType']):
        count (int):
    """

    machine_types: list["MachineType"]
    count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        machine_types = []
        for machine_types_item_data in self.machine_types:
            machine_types_item = machine_types_item_data.to_dict()
            machine_types.append(machine_types_item)

        count = self.count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "machine_types": machine_types,
                "count": count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.machine_type import MachineType

        d = dict(src_dict)
        machine_types = []
        _machine_types = d.pop("machine_types")
        for machine_types_item_data in _machine_types:
            machine_types_item = MachineType.from_dict(machine_types_item_data)

            machine_types.append(machine_types_item)

        count = d.pop("count")

        machine_types_response = cls(
            machine_types=machine_types,
            count=count,
        )

        machine_types_response.additional_properties = d
        return machine_types_response

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
