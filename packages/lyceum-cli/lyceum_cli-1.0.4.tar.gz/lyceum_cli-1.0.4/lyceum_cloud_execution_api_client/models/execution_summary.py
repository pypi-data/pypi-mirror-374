from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExecutionSummary")


@_attrs_define
class ExecutionSummary:
    """Summary model for execution information.

    Attributes:
        execution_id (str):
        status (str):
        execution_type (str):
        hardware_profile (str):
        created_at (str):
        execution_owner (Union[None, Unset, str]):
    """

    execution_id: str
    status: str
    execution_type: str
    hardware_profile: str
    created_at: str
    execution_owner: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        execution_id = self.execution_id

        status = self.status

        execution_type = self.execution_type

        hardware_profile = self.hardware_profile

        created_at = self.created_at

        execution_owner: Union[None, Unset, str]
        if isinstance(self.execution_owner, Unset):
            execution_owner = UNSET
        else:
            execution_owner = self.execution_owner

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "execution_id": execution_id,
                "status": status,
                "execution_type": execution_type,
                "hardware_profile": hardware_profile,
                "created_at": created_at,
            }
        )
        if execution_owner is not UNSET:
            field_dict["execution_owner"] = execution_owner

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        execution_id = d.pop("execution_id")

        status = d.pop("status")

        execution_type = d.pop("execution_type")

        hardware_profile = d.pop("hardware_profile")

        created_at = d.pop("created_at")

        def _parse_execution_owner(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        execution_owner = _parse_execution_owner(d.pop("execution_owner", UNSET))

        execution_summary = cls(
            execution_id=execution_id,
            status=status,
            execution_type=execution_type,
            hardware_profile=hardware_profile,
            created_at=created_at,
            execution_owner=execution_owner,
        )

        execution_summary.additional_properties = d
        return execution_summary

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
