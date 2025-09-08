from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_descriptor_values import MessageDescriptorValues


T = TypeVar("T", bound="MessageDescriptor")


@_attrs_define
class MessageDescriptor:
    """
    Attributes:
        id (Union[Unset, str]): The i18n message ID
        default_message (Union[Unset, str]): The default message text
        values (Union[Unset, MessageDescriptorValues]): Optional values for message interpolation
    """

    id: Union[Unset, str] = UNSET
    default_message: Union[Unset, str] = UNSET
    values: Union[Unset, "MessageDescriptorValues"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        default_message = self.default_message

        values: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.values, Unset):
            values = self.values.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if default_message is not UNSET:
            field_dict["defaultMessage"] = default_message
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_descriptor_values import MessageDescriptorValues

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        default_message = d.pop("defaultMessage", UNSET)

        _values = d.pop("values", UNSET)
        values: Union[Unset, MessageDescriptorValues]
        if isinstance(_values, Unset):
            values = UNSET
        else:
            values = MessageDescriptorValues.from_dict(_values)

        message_descriptor = cls(
            id=id,
            default_message=default_message,
            values=values,
        )

        message_descriptor.additional_properties = d
        return message_descriptor

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
