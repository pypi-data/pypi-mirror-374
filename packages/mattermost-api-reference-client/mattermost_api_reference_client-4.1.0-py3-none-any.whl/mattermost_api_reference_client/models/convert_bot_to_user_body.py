from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.convert_bot_to_user_body_props import ConvertBotToUserBodyProps
    from ..models.user_notify_props import UserNotifyProps


T = TypeVar("T", bound="ConvertBotToUserBody")


@_attrs_define
class ConvertBotToUserBody:
    """
    Attributes:
        email (Union[Unset, str]):
        username (Union[Unset, str]):
        password (Union[Unset, str]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        nickname (Union[Unset, str]):
        locale (Union[Unset, str]):
        position (Union[Unset, str]):
        props (Union[Unset, ConvertBotToUserBodyProps]):
        notify_props (Union[Unset, UserNotifyProps]):
    """

    email: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    nickname: Union[Unset, str] = UNSET
    locale: Union[Unset, str] = UNSET
    position: Union[Unset, str] = UNSET
    props: Union[Unset, "ConvertBotToUserBodyProps"] = UNSET
    notify_props: Union[Unset, "UserNotifyProps"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        username = self.username

        password = self.password

        first_name = self.first_name

        last_name = self.last_name

        nickname = self.nickname

        locale = self.locale

        position = self.position

        props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        notify_props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.notify_props, Unset):
            notify_props = self.notify_props.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if username is not UNSET:
            field_dict["username"] = username
        if password is not UNSET:
            field_dict["password"] = password
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if locale is not UNSET:
            field_dict["locale"] = locale
        if position is not UNSET:
            field_dict["position"] = position
        if props is not UNSET:
            field_dict["props"] = props
        if notify_props is not UNSET:
            field_dict["notify_props"] = notify_props

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.convert_bot_to_user_body_props import ConvertBotToUserBodyProps
        from ..models.user_notify_props import UserNotifyProps

        d = dict(src_dict)
        email = d.pop("email", UNSET)

        username = d.pop("username", UNSET)

        password = d.pop("password", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        nickname = d.pop("nickname", UNSET)

        locale = d.pop("locale", UNSET)

        position = d.pop("position", UNSET)

        _props = d.pop("props", UNSET)
        props: Union[Unset, ConvertBotToUserBodyProps]
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = ConvertBotToUserBodyProps.from_dict(_props)

        _notify_props = d.pop("notify_props", UNSET)
        notify_props: Union[Unset, UserNotifyProps]
        if isinstance(_notify_props, Unset):
            notify_props = UNSET
        else:
            notify_props = UserNotifyProps.from_dict(_notify_props)

        convert_bot_to_user_body = cls(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            locale=locale,
            position=position,
            props=props,
            notify_props=notify_props,
        )

        convert_bot_to_user_body.additional_properties = d
        return convert_bot_to_user_body

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
