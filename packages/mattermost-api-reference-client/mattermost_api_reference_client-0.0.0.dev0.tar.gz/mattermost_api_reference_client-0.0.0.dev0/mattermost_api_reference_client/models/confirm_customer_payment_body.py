from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfirmCustomerPaymentBody")


@_attrs_define
class ConfirmCustomerPaymentBody:
    """
    Attributes:
        stripe_setup_intent_id (Union[Unset, str]):
    """

    stripe_setup_intent_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stripe_setup_intent_id = self.stripe_setup_intent_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if stripe_setup_intent_id is not UNSET:
            field_dict["stripe_setup_intent_id"] = stripe_setup_intent_id

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.stripe_setup_intent_id, Unset):
            files.append(("stripe_setup_intent_id", (None, str(self.stripe_setup_intent_id).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stripe_setup_intent_id = d.pop("stripe_setup_intent_id", UNSET)

        confirm_customer_payment_body = cls(
            stripe_setup_intent_id=stripe_setup_intent_id,
        )

        confirm_customer_payment_body.additional_properties = d
        return confirm_customer_payment_body

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
