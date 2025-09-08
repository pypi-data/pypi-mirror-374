from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="GetUsersByGroupChannelIdsResponse200")


@_attrs_define
class GetUsersByGroupChannelIdsResponse200:
    """
    Attributes:
        channel_id (Union[Unset, list['User']]):
    """

    channel_id: Union[Unset, list["User"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_id: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.channel_id, Unset):
            channel_id = []
            for channel_id_item_data in self.channel_id:
                channel_id_item = channel_id_item_data.to_dict()
                channel_id.append(channel_id_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if channel_id is not UNSET:
            field_dict["<CHANNEL_ID>"] = channel_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        channel_id = []
        _channel_id = d.pop("<CHANNEL_ID>", UNSET)
        for channel_id_item_data in _channel_id or []:
            channel_id_item = User.from_dict(channel_id_item_data)

            channel_id.append(channel_id_item)

        get_users_by_group_channel_ids_response_200 = cls(
            channel_id=channel_id,
        )

        get_users_by_group_channel_ids_response_200.additional_properties = d
        return get_users_by_group_channel_ids_response_200

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
