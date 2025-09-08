from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UpdateTeamBody")


@_attrs_define
class UpdateTeamBody:
    """
    Attributes:
        id (str):
        display_name (str):
        description (str):
        company_name (str):
        allowed_domains (str):
        invite_id (str):
        allow_open_invite (str):
    """

    id: str
    display_name: str
    description: str
    company_name: str
    allowed_domains: str
    invite_id: str
    allow_open_invite: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_name = self.display_name

        description = self.description

        company_name = self.company_name

        allowed_domains = self.allowed_domains

        invite_id = self.invite_id

        allow_open_invite = self.allow_open_invite

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "display_name": display_name,
                "description": description,
                "company_name": company_name,
                "allowed_domains": allowed_domains,
                "invite_id": invite_id,
                "allow_open_invite": allow_open_invite,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        display_name = d.pop("display_name")

        description = d.pop("description")

        company_name = d.pop("company_name")

        allowed_domains = d.pop("allowed_domains")

        invite_id = d.pop("invite_id")

        allow_open_invite = d.pop("allow_open_invite")

        update_team_body = cls(
            id=id,
            display_name=display_name,
            description=description,
            company_name=company_name,
            allowed_domains=allowed_domains,
            invite_id=invite_id,
            allow_open_invite=allow_open_invite,
        )

        update_team_body.additional_properties = d
        return update_team_body

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
