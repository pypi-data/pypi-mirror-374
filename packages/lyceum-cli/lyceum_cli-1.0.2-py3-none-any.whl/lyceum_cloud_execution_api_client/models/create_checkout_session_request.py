from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateCheckoutSessionRequest")


@_attrs_define
class CreateCheckoutSessionRequest:
    """
    Attributes:
        amount (int):
        currency (Union[Unset, str]):  Default: 'eur'.
        description (Union[Unset, str]):  Default: 'Lyceum Cloud Credits'.
    """

    amount: int
    currency: Union[Unset, str] = "eur"
    description: Union[Unset, str] = "Lyceum Cloud Credits"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        currency = self.currency

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
            }
        )
        if currency is not UNSET:
            field_dict["currency"] = currency
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount")

        currency = d.pop("currency", UNSET)

        description = d.pop("description", UNSET)

        create_checkout_session_request = cls(
            amount=amount,
            currency=currency,
            description=description,
        )

        create_checkout_session_request.additional_properties = d
        return create_checkout_session_request

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
