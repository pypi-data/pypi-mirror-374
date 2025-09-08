from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SubscriptionStats")


@_attrs_define
class SubscriptionStats:
    """
    Attributes:
        remaining_seats (Union[Unset, int]):
        is_paid_tier (Union[Unset, str]):
    """

    remaining_seats: Union[Unset, int] = UNSET
    is_paid_tier: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        remaining_seats = self.remaining_seats

        is_paid_tier = self.is_paid_tier

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if remaining_seats is not UNSET:
            field_dict["remaining_seats"] = remaining_seats
        if is_paid_tier is not UNSET:
            field_dict["is_paid_tier"] = is_paid_tier

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        remaining_seats = d.pop("remaining_seats", UNSET)

        is_paid_tier = d.pop("is_paid_tier", UNSET)

        subscription_stats = cls(
            remaining_seats=remaining_seats,
            is_paid_tier=is_paid_tier,
        )

        subscription_stats.additional_properties = d
        return subscription_stats

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
