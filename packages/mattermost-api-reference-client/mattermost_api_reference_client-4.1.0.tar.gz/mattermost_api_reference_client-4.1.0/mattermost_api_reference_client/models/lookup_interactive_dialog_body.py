from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.lookup_interactive_dialog_body_submission import LookupInteractiveDialogBodySubmission


T = TypeVar("T", bound="LookupInteractiveDialogBody")


@_attrs_define
class LookupInteractiveDialogBody:
    """
    Attributes:
        url (str): The URL to send the lookup request to
        channel_id (str): Channel ID the user is performing the lookup from
        team_id (str): Team ID the user is performing the lookup from
        submission (LookupInteractiveDialogBodySubmission): String map where keys are element names and values are the
            element input values
        callback_id (Union[Unset, str]): Callback ID sent when the dialog was opened
        state (Union[Unset, str]): State sent when the dialog was opened
    """

    url: str
    channel_id: str
    team_id: str
    submission: "LookupInteractiveDialogBodySubmission"
    callback_id: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        channel_id = self.channel_id

        team_id = self.team_id

        submission = self.submission.to_dict()

        callback_id = self.callback_id

        state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "channel_id": channel_id,
                "team_id": team_id,
                "submission": submission,
            }
        )
        if callback_id is not UNSET:
            field_dict["callback_id"] = callback_id
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.lookup_interactive_dialog_body_submission import LookupInteractiveDialogBodySubmission

        d = dict(src_dict)
        url = d.pop("url")

        channel_id = d.pop("channel_id")

        team_id = d.pop("team_id")

        submission = LookupInteractiveDialogBodySubmission.from_dict(d.pop("submission"))

        callback_id = d.pop("callback_id", UNSET)

        state = d.pop("state", UNSET)

        lookup_interactive_dialog_body = cls(
            url=url,
            channel_id=channel_id,
            team_id=team_id,
            submission=submission,
            callback_id=callback_id,
            state=state,
        )

        lookup_interactive_dialog_body.additional_properties = d
        return lookup_interactive_dialog_body

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
