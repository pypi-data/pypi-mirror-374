from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreditsBalance")


@_attrs_define
class CreditsBalance:
    """
    Attributes:
        available_credits (float):
        used_credits (float):
        total_credits_used (float):
        remaining_credits (float):
    """

    available_credits: float
    used_credits: float
    total_credits_used: float
    remaining_credits: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        available_credits = self.available_credits

        used_credits = self.used_credits

        total_credits_used = self.total_credits_used

        remaining_credits = self.remaining_credits

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "available_credits": available_credits,
                "used_credits": used_credits,
                "total_credits_used": total_credits_used,
                "remaining_credits": remaining_credits,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        available_credits = d.pop("available_credits")

        used_credits = d.pop("used_credits")

        total_credits_used = d.pop("total_credits_used")

        remaining_credits = d.pop("remaining_credits")

        credits_balance = cls(
            available_credits=available_credits,
            used_credits=used_credits,
            total_credits_used=total_credits_used,
            remaining_credits=remaining_credits,
        )

        credits_balance.additional_properties = d
        return credits_balance

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
