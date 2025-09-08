from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BoardsLimits")


@_attrs_define
class BoardsLimits:
    """
    Attributes:
        cards (Union[None, Unset, int]):
        views (Union[None, Unset, int]):
    """

    cards: Union[None, Unset, int] = UNSET
    views: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cards: Union[None, Unset, int]
        if isinstance(self.cards, Unset):
            cards = UNSET
        else:
            cards = self.cards

        views: Union[None, Unset, int]
        if isinstance(self.views, Unset):
            views = UNSET
        else:
            views = self.views

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cards is not UNSET:
            field_dict["cards"] = cards
        if views is not UNSET:
            field_dict["views"] = views

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_cards(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        cards = _parse_cards(d.pop("cards", UNSET))

        def _parse_views(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        views = _parse_views(d.pop("views", UNSET))

        boards_limits = cls(
            cards=cards,
            views=views,
        )

        boards_limits.additional_properties = d
        return boards_limits

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
