import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserCredits")


@_attrs_define
class UserCredits:
    """
    Attributes:
        user_id (str):
        email (str):
        available_credits (float):
        used_credits (float):
        total_credits_used (float):
        created_at (datetime.datetime):
        last_updated (datetime.datetime):
        stripe_customer_id (Union[None, Unset, str]):
    """

    user_id: str
    email: str
    available_credits: float
    used_credits: float
    total_credits_used: float
    created_at: datetime.datetime
    last_updated: datetime.datetime
    stripe_customer_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        email = self.email

        available_credits = self.available_credits

        used_credits = self.used_credits

        total_credits_used = self.total_credits_used

        created_at = self.created_at.isoformat()

        last_updated = self.last_updated.isoformat()

        stripe_customer_id: Union[None, Unset, str]
        if isinstance(self.stripe_customer_id, Unset):
            stripe_customer_id = UNSET
        else:
            stripe_customer_id = self.stripe_customer_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "email": email,
                "available_credits": available_credits,
                "used_credits": used_credits,
                "total_credits_used": total_credits_used,
                "created_at": created_at,
                "last_updated": last_updated,
            }
        )
        if stripe_customer_id is not UNSET:
            field_dict["stripe_customer_id"] = stripe_customer_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        email = d.pop("email")

        available_credits = d.pop("available_credits")

        used_credits = d.pop("used_credits")

        total_credits_used = d.pop("total_credits_used")

        created_at = isoparse(d.pop("created_at"))

        last_updated = isoparse(d.pop("last_updated"))

        def _parse_stripe_customer_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        stripe_customer_id = _parse_stripe_customer_id(d.pop("stripe_customer_id", UNSET))

        user_credits = cls(
            user_id=user_id,
            email=email,
            available_credits=available_credits,
            used_credits=used_credits,
            total_credits_used=total_credits_used,
            created_at=created_at,
            last_updated=last_updated,
            stripe_customer_id=stripe_customer_id,
        )

        user_credits.additional_properties = d
        return user_credits

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
