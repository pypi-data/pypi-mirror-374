from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_post_body_metadata_priority import CreatePostBodyMetadataPriority


T = TypeVar("T", bound="CreatePostBodyMetadata")


@_attrs_define
class CreatePostBodyMetadata:
    """A JSON object to add post metadata, e.g the post's priority

    Attributes:
        priority (Union[Unset, CreatePostBodyMetadataPriority]): An object containing the post's priority properties
    """

    priority: Union[Unset, "CreatePostBodyMetadataPriority"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        priority: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.priority, Unset):
            priority = self.priority.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_post_body_metadata_priority import CreatePostBodyMetadataPriority

        d = dict(src_dict)
        _priority = d.pop("priority", UNSET)
        priority: Union[Unset, CreatePostBodyMetadataPriority]
        if isinstance(_priority, Unset):
            priority = UNSET
        else:
            priority = CreatePostBodyMetadataPriority.from_dict(_priority)

        create_post_body_metadata = cls(
            priority=priority,
        )

        create_post_body_metadata.additional_properties = d
        return create_post_body_metadata

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
