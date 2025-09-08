from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="UserAutocompleteInChannel")


@_attrs_define
class UserAutocompleteInChannel:
    """
    Attributes:
        in_channel (Union[Unset, list['User']]): A list of user objects in the channel
        out_of_channel (Union[Unset, list['User']]): A list of user objects not in the channel
    """

    in_channel: Union[Unset, list["User"]] = UNSET
    out_of_channel: Union[Unset, list["User"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        in_channel: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.in_channel, Unset):
            in_channel = []
            for in_channel_item_data in self.in_channel:
                in_channel_item = in_channel_item_data.to_dict()
                in_channel.append(in_channel_item)

        out_of_channel: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.out_of_channel, Unset):
            out_of_channel = []
            for out_of_channel_item_data in self.out_of_channel:
                out_of_channel_item = out_of_channel_item_data.to_dict()
                out_of_channel.append(out_of_channel_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if in_channel is not UNSET:
            field_dict["in_channel"] = in_channel
        if out_of_channel is not UNSET:
            field_dict["out_of_channel"] = out_of_channel

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        in_channel = []
        _in_channel = d.pop("in_channel", UNSET)
        for in_channel_item_data in _in_channel or []:
            in_channel_item = User.from_dict(in_channel_item_data)

            in_channel.append(in_channel_item)

        out_of_channel = []
        _out_of_channel = d.pop("out_of_channel", UNSET)
        for out_of_channel_item_data in _out_of_channel or []:
            out_of_channel_item = User.from_dict(out_of_channel_item_data)

            out_of_channel.append(out_of_channel_item)

        user_autocomplete_in_channel = cls(
            in_channel=in_channel,
            out_of_channel=out_of_channel,
        )

        user_autocomplete_in_channel.additional_properties = d
        return user_autocomplete_in_channel

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
