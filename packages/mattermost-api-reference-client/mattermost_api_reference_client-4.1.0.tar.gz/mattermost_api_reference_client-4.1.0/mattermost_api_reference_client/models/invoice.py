from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.invoice_line_item import InvoiceLineItem


T = TypeVar("T", bound="Invoice")


@_attrs_define
class Invoice:
    """
    Attributes:
        id (Union[Unset, str]):
        number (Union[Unset, str]):
        create_at (Union[Unset, int]):
        total (Union[Unset, int]):
        tax (Union[Unset, int]):
        status (Union[Unset, str]):
        period_start (Union[Unset, int]):
        period_end (Union[Unset, int]):
        subscription_id (Union[Unset, str]):
        item (Union[Unset, list['InvoiceLineItem']]):
    """

    id: Union[Unset, str] = UNSET
    number: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    total: Union[Unset, int] = UNSET
    tax: Union[Unset, int] = UNSET
    status: Union[Unset, str] = UNSET
    period_start: Union[Unset, int] = UNSET
    period_end: Union[Unset, int] = UNSET
    subscription_id: Union[Unset, str] = UNSET
    item: Union[Unset, list["InvoiceLineItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        number = self.number

        create_at = self.create_at

        total = self.total

        tax = self.tax

        status = self.status

        period_start = self.period_start

        period_end = self.period_end

        subscription_id = self.subscription_id

        item: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.item, Unset):
            item = []
            for item_item_data in self.item:
                item_item = item_item_data.to_dict()
                item.append(item_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if number is not UNSET:
            field_dict["number"] = number
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if total is not UNSET:
            field_dict["total"] = total
        if tax is not UNSET:
            field_dict["tax"] = tax
        if status is not UNSET:
            field_dict["status"] = status
        if period_start is not UNSET:
            field_dict["period_start"] = period_start
        if period_end is not UNSET:
            field_dict["period_end"] = period_end
        if subscription_id is not UNSET:
            field_dict["subscription_id"] = subscription_id
        if item is not UNSET:
            field_dict["item"] = item

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.invoice_line_item import InvoiceLineItem

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        number = d.pop("number", UNSET)

        create_at = d.pop("create_at", UNSET)

        total = d.pop("total", UNSET)

        tax = d.pop("tax", UNSET)

        status = d.pop("status", UNSET)

        period_start = d.pop("period_start", UNSET)

        period_end = d.pop("period_end", UNSET)

        subscription_id = d.pop("subscription_id", UNSET)

        item = []
        _item = d.pop("item", UNSET)
        for item_item_data in _item or []:
            item_item = InvoiceLineItem.from_dict(item_item_data)

            item.append(item_item)

        invoice = cls(
            id=id,
            number=number,
            create_at=create_at,
            total=total,
            tax=tax,
            status=status,
            period_start=period_start,
            period_end=period_end,
            subscription_id=subscription_id,
            item=item,
        )

        invoice.additional_properties = d
        return invoice

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
