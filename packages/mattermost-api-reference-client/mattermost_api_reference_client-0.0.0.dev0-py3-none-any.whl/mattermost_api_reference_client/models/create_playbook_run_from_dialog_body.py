from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_playbook_run_from_dialog_body_submission import CreatePlaybookRunFromDialogBodySubmission


T = TypeVar("T", bound="CreatePlaybookRunFromDialogBody")


@_attrs_define
class CreatePlaybookRunFromDialogBody:
    """
    Attributes:
        type_ (Union[Unset, str]):  Example: dialog_submission.
        url (Union[Unset, str]):
        callback_id (Union[Unset, str]): Callback ID provided by the integration.
        state (Union[Unset, str]): Stringified JSON with the post_id and the client_id.
        user_id (Union[Unset, str]): ID of the user who submitted the dialog.
        channel_id (Union[Unset, str]): ID of the channel the user was in when submitting the dialog.
        team_id (Union[Unset, str]): ID of the team the user was on when submitting the dialog.
        submission (Union[Unset, CreatePlaybookRunFromDialogBodySubmission]): Map of the dialog fields to their values
        cancelled (Union[Unset, bool]): If the dialog was cancelled.
    """

    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    callback_id: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    team_id: Union[Unset, str] = UNSET
    submission: Union[Unset, "CreatePlaybookRunFromDialogBodySubmission"] = UNSET
    cancelled: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        url = self.url

        callback_id = self.callback_id

        state = self.state

        user_id = self.user_id

        channel_id = self.channel_id

        team_id = self.team_id

        submission: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.submission, Unset):
            submission = self.submission.to_dict()

        cancelled = self.cancelled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if callback_id is not UNSET:
            field_dict["callback_id"] = callback_id
        if state is not UNSET:
            field_dict["state"] = state
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if submission is not UNSET:
            field_dict["submission"] = submission
        if cancelled is not UNSET:
            field_dict["cancelled"] = cancelled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_playbook_run_from_dialog_body_submission import CreatePlaybookRunFromDialogBodySubmission

        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        callback_id = d.pop("callback_id", UNSET)

        state = d.pop("state", UNSET)

        user_id = d.pop("user_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        team_id = d.pop("team_id", UNSET)

        _submission = d.pop("submission", UNSET)
        submission: Union[Unset, CreatePlaybookRunFromDialogBodySubmission]
        if isinstance(_submission, Unset):
            submission = UNSET
        else:
            submission = CreatePlaybookRunFromDialogBodySubmission.from_dict(_submission)

        cancelled = d.pop("cancelled", UNSET)

        create_playbook_run_from_dialog_body = cls(
            type_=type_,
            url=url,
            callback_id=callback_id,
            state=state,
            user_id=user_id,
            channel_id=channel_id,
            team_id=team_id,
            submission=submission,
            cancelled=cancelled,
        )

        create_playbook_run_from_dialog_body.additional_properties = d
        return create_playbook_run_from_dialog_body

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
