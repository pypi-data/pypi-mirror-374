from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Notice")


@_attrs_define
class Notice:
    """
    Attributes:
        id (Union[Unset, str]): Notice ID
        sys_admin_only (Union[Unset, bool]): Does this notice apply only to sysadmins
        team_admin_only (Union[Unset, bool]): Does this notice apply only to team admins
        action (Union[Unset, str]): Optional action to perform on action button click. (defaults to closing the notice)
        action_param (Union[Unset, str]): Optional action parameter.
            Example: {"action": "url", actionParam: "/console/some-page"}
        action_text (Union[Unset, str]): Optional override for the action button text (defaults to OK)
        description (Union[Unset, str]): Notice content. Use {{Mattermost}} instead of plain text to support white-
            labeling. Text supports Markdown.
        image (Union[Unset, str]): URL of image to display
        title (Union[Unset, str]): Notice title. Use {{Mattermost}} instead of plain text to support white-labeling.
            Text supports Markdown.
    """

    id: Union[Unset, str] = UNSET
    sys_admin_only: Union[Unset, bool] = UNSET
    team_admin_only: Union[Unset, bool] = UNSET
    action: Union[Unset, str] = UNSET
    action_param: Union[Unset, str] = UNSET
    action_text: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    image: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        sys_admin_only = self.sys_admin_only

        team_admin_only = self.team_admin_only

        action = self.action

        action_param = self.action_param

        action_text = self.action_text

        description = self.description

        image = self.image

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if sys_admin_only is not UNSET:
            field_dict["sysAdminOnly"] = sys_admin_only
        if team_admin_only is not UNSET:
            field_dict["teamAdminOnly"] = team_admin_only
        if action is not UNSET:
            field_dict["action"] = action
        if action_param is not UNSET:
            field_dict["actionParam"] = action_param
        if action_text is not UNSET:
            field_dict["actionText"] = action_text
        if description is not UNSET:
            field_dict["description"] = description
        if image is not UNSET:
            field_dict["image"] = image
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        sys_admin_only = d.pop("sysAdminOnly", UNSET)

        team_admin_only = d.pop("teamAdminOnly", UNSET)

        action = d.pop("action", UNSET)

        action_param = d.pop("actionParam", UNSET)

        action_text = d.pop("actionText", UNSET)

        description = d.pop("description", UNSET)

        image = d.pop("image", UNSET)

        title = d.pop("title", UNSET)

        notice = cls(
            id=id,
            sys_admin_only=sys_admin_only,
            team_admin_only=team_admin_only,
            action=action,
            action_param=action_param,
            action_text=action_text,
            description=description,
            image=image,
            title=title,
        )

        notice.additional_properties = d
        return notice

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
