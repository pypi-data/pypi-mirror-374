from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.open_interactive_dialog_body_dialog_elements_item import OpenInteractiveDialogBodyDialogElementsItem


T = TypeVar("T", bound="OpenInteractiveDialogBodyDialog")


@_attrs_define
class OpenInteractiveDialogBodyDialog:
    """Post object to create

    Attributes:
        title (str): Title of the dialog
        elements (list['OpenInteractiveDialogBodyDialogElementsItem']): Input elements, see
            https://docs.mattermost.com/developer/interactive-dialogs.html#elements
        callback_id (Union[Unset, str]): Set an ID that will be included when the dialog is submitted
        introduction_text (Union[Unset, str]): Markdown formatted introductory paragraph
        submit_label (Union[Unset, str]): Label on the submit button
        notify_on_cancel (Union[Unset, bool]): Set true to receive payloads when user cancels a dialog
        state (Union[Unset, str]): Set some state to be echoed back with the dialog submission
    """

    title: str
    elements: list["OpenInteractiveDialogBodyDialogElementsItem"]
    callback_id: Union[Unset, str] = UNSET
    introduction_text: Union[Unset, str] = UNSET
    submit_label: Union[Unset, str] = UNSET
    notify_on_cancel: Union[Unset, bool] = UNSET
    state: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        elements = []
        for elements_item_data in self.elements:
            elements_item = elements_item_data.to_dict()
            elements.append(elements_item)

        callback_id = self.callback_id

        introduction_text = self.introduction_text

        submit_label = self.submit_label

        notify_on_cancel = self.notify_on_cancel

        state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "elements": elements,
            }
        )
        if callback_id is not UNSET:
            field_dict["callback_id"] = callback_id
        if introduction_text is not UNSET:
            field_dict["introduction_text"] = introduction_text
        if submit_label is not UNSET:
            field_dict["submit_label"] = submit_label
        if notify_on_cancel is not UNSET:
            field_dict["notify_on_cancel"] = notify_on_cancel
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_interactive_dialog_body_dialog_elements_item import (
            OpenInteractiveDialogBodyDialogElementsItem,
        )

        d = dict(src_dict)
        title = d.pop("title")

        elements = []
        _elements = d.pop("elements")
        for elements_item_data in _elements:
            elements_item = OpenInteractiveDialogBodyDialogElementsItem.from_dict(elements_item_data)

            elements.append(elements_item)

        callback_id = d.pop("callback_id", UNSET)

        introduction_text = d.pop("introduction_text", UNSET)

        submit_label = d.pop("submit_label", UNSET)

        notify_on_cancel = d.pop("notify_on_cancel", UNSET)

        state = d.pop("state", UNSET)

        open_interactive_dialog_body_dialog = cls(
            title=title,
            elements=elements,
            callback_id=callback_id,
            introduction_text=introduction_text,
            submit_label=submit_label,
            notify_on_cancel=notify_on_cancel,
            state=state,
        )

        open_interactive_dialog_body_dialog.additional_properties = d
        return open_interactive_dialog_body_dialog

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
