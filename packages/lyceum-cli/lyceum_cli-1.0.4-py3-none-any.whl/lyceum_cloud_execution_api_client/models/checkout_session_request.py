from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CheckoutSessionRequest")


@_attrs_define
class CheckoutSessionRequest:
    """
    Attributes:
        credits_amount (int):
        success_url (Union[None, Unset, str]):
        cancel_url (Union[None, Unset, str]):
    """

    credits_amount: int
    success_url: Union[None, Unset, str] = UNSET
    cancel_url: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        credits_amount = self.credits_amount

        success_url: Union[None, Unset, str]
        if isinstance(self.success_url, Unset):
            success_url = UNSET
        else:
            success_url = self.success_url

        cancel_url: Union[None, Unset, str]
        if isinstance(self.cancel_url, Unset):
            cancel_url = UNSET
        else:
            cancel_url = self.cancel_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "credits_amount": credits_amount,
            }
        )
        if success_url is not UNSET:
            field_dict["success_url"] = success_url
        if cancel_url is not UNSET:
            field_dict["cancel_url"] = cancel_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        credits_amount = d.pop("credits_amount")

        def _parse_success_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        success_url = _parse_success_url(d.pop("success_url", UNSET))

        def _parse_cancel_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cancel_url = _parse_cancel_url(d.pop("cancel_url", UNSET))

        checkout_session_request = cls(
            credits_amount=credits_amount,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        checkout_session_request.additional_properties = d
        return checkout_session_request

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
