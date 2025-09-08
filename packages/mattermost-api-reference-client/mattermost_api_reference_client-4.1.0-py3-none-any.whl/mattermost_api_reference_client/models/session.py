from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.session_props import SessionProps
    from ..models.team_member import TeamMember


T = TypeVar("T", bound="Session")


@_attrs_define
class Session:
    """
    Attributes:
        create_at (Union[Unset, int]): The time in milliseconds a session was created
        device_id (Union[Unset, str]):
        expires_at (Union[Unset, int]): The time in milliseconds a session will expire
        id (Union[Unset, str]):
        is_oauth (Union[Unset, bool]):
        last_activity_at (Union[Unset, int]): The time in milliseconds of the last activity of a session
        props (Union[Unset, SessionProps]):
        roles (Union[Unset, str]):
        team_members (Union[Unset, list['TeamMember']]):
        token (Union[Unset, str]):
        user_id (Union[Unset, str]):
    """

    create_at: Union[Unset, int] = UNSET
    device_id: Union[Unset, str] = UNSET
    expires_at: Union[Unset, int] = UNSET
    id: Union[Unset, str] = UNSET
    is_oauth: Union[Unset, bool] = UNSET
    last_activity_at: Union[Unset, int] = UNSET
    props: Union[Unset, "SessionProps"] = UNSET
    roles: Union[Unset, str] = UNSET
    team_members: Union[Unset, list["TeamMember"]] = UNSET
    token: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        create_at = self.create_at

        device_id = self.device_id

        expires_at = self.expires_at

        id = self.id

        is_oauth = self.is_oauth

        last_activity_at = self.last_activity_at

        props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        roles = self.roles

        team_members: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.team_members, Unset):
            team_members = []
            for team_members_item_data in self.team_members:
                team_members_item = team_members_item_data.to_dict()
                team_members.append(team_members_item)

        token = self.token

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if id is not UNSET:
            field_dict["id"] = id
        if is_oauth is not UNSET:
            field_dict["is_oauth"] = is_oauth
        if last_activity_at is not UNSET:
            field_dict["last_activity_at"] = last_activity_at
        if props is not UNSET:
            field_dict["props"] = props
        if roles is not UNSET:
            field_dict["roles"] = roles
        if team_members is not UNSET:
            field_dict["team_members"] = team_members
        if token is not UNSET:
            field_dict["token"] = token
        if user_id is not UNSET:
            field_dict["user_id"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.session_props import SessionProps
        from ..models.team_member import TeamMember

        d = dict(src_dict)
        create_at = d.pop("create_at", UNSET)

        device_id = d.pop("device_id", UNSET)

        expires_at = d.pop("expires_at", UNSET)

        id = d.pop("id", UNSET)

        is_oauth = d.pop("is_oauth", UNSET)

        last_activity_at = d.pop("last_activity_at", UNSET)

        _props = d.pop("props", UNSET)
        props: Union[Unset, SessionProps]
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = SessionProps.from_dict(_props)

        roles = d.pop("roles", UNSET)

        team_members = []
        _team_members = d.pop("team_members", UNSET)
        for team_members_item_data in _team_members or []:
            team_members_item = TeamMember.from_dict(team_members_item_data)

            team_members.append(team_members_item)

        token = d.pop("token", UNSET)

        user_id = d.pop("user_id", UNSET)

        session = cls(
            create_at=create_at,
            device_id=device_id,
            expires_at=expires_at,
            id=id,
            is_oauth=is_oauth,
            last_activity_at=last_activity_at,
            props=props,
            roles=roles,
            team_members=team_members,
            token=token,
            user_id=user_id,
        )

        session.additional_properties = d
        return session

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
