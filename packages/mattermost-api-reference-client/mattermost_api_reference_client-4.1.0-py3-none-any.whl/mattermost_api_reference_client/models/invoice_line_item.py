from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InvoiceLineItem")


@_attrs_define
class InvoiceLineItem:
    """
    Attributes:
        price_id (Union[Unset, str]):
        total (Union[Unset, int]):
        quantity (Union[Unset, int]):
        price_per_unit (Union[Unset, int]):
        description (Union[Unset, str]):
        metadata (Union[Unset, list[str]]):
    """

    price_id: Union[Unset, str] = UNSET
    total: Union[Unset, int] = UNSET
    quantity: Union[Unset, int] = UNSET
    price_per_unit: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    metadata: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        price_id = self.price_id

        total = self.total

        quantity = self.quantity

        price_per_unit = self.price_per_unit

        description = self.description

        metadata: Union[Unset, list[str]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if price_id is not UNSET:
            field_dict["price_id"] = price_id
        if total is not UNSET:
            field_dict["total"] = total
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if price_per_unit is not UNSET:
            field_dict["price_per_unit"] = price_per_unit
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        price_id = d.pop("price_id", UNSET)

        total = d.pop("total", UNSET)

        quantity = d.pop("quantity", UNSET)

        price_per_unit = d.pop("price_per_unit", UNSET)

        description = d.pop("description", UNSET)

        metadata = cast(list[str], d.pop("metadata", UNSET))

        invoice_line_item = cls(
            price_id=price_id,
            total=total,
            quantity=quantity,
            price_per_unit=price_per_unit,
            description=description,
            metadata=metadata,
        )

        invoice_line_item.additional_properties = d
        return invoice_line_item

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
