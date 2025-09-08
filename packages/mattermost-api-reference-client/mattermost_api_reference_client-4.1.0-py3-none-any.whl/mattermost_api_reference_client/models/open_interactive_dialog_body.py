from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.open_interactive_dialog_body_dialog import OpenInteractiveDialogBodyDialog


T = TypeVar("T", bound="OpenInteractiveDialogBody")


@_attrs_define
class OpenInteractiveDialogBody:
    """
    Attributes:
        trigger_id (str): Trigger ID provided by other action
        url (str): The URL to send the submitted dialog payload to
        dialog (OpenInteractiveDialogBodyDialog): Post object to create
    """

    trigger_id: str
    url: str
    dialog: "OpenInteractiveDialogBodyDialog"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        trigger_id = self.trigger_id

        url = self.url

        dialog = self.dialog.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "trigger_id": trigger_id,
                "url": url,
                "dialog": dialog,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_interactive_dialog_body_dialog import OpenInteractiveDialogBodyDialog

        d = dict(src_dict)
        trigger_id = d.pop("trigger_id")

        url = d.pop("url")

        dialog = OpenInteractiveDialogBodyDialog.from_dict(d.pop("dialog"))

        open_interactive_dialog_body = cls(
            trigger_id=trigger_id,
            url=url,
            dialog=dialog,
        )

        open_interactive_dialog_body.additional_properties = d
        return open_interactive_dialog_body

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
