from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="UserAutocompleteInTeam")


@_attrs_define
class UserAutocompleteInTeam:
    """
    Attributes:
        in_team (Union[Unset, list['User']]): A list of user objects in the team
    """

    in_team: Union[Unset, list["User"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        in_team: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.in_team, Unset):
            in_team = []
            for in_team_item_data in self.in_team:
                in_team_item = in_team_item_data.to_dict()
                in_team.append(in_team_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if in_team is not UNSET:
            field_dict["in_team"] = in_team

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        in_team = []
        _in_team = d.pop("in_team", UNSET)
        for in_team_item_data in _in_team or []:
            in_team_item = User.from_dict(in_team_item_data)

            in_team.append(in_team_item)

        user_autocomplete_in_team = cls(
            in_team=in_team,
        )

        user_autocomplete_in_team.additional_properties = d
        return user_autocomplete_in_team

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
