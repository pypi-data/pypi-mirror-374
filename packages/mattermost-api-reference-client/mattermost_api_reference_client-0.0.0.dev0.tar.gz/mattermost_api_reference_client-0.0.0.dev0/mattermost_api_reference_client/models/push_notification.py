from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PushNotification")


@_attrs_define
class PushNotification:
    """
    Attributes:
        ack_id (Union[Unset, str]):
        platform (Union[Unset, str]):
        server_id (Union[Unset, str]):
        device_id (Union[Unset, str]):
        post_id (Union[Unset, str]):
        category (Union[Unset, str]):
        sound (Union[Unset, str]):
        message (Union[Unset, str]):
        badge (Union[Unset, float]):
        cont_ava (Union[Unset, float]):
        team_id (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        root_id (Union[Unset, str]):
        channel_name (Union[Unset, str]):
        type_ (Union[Unset, str]):
        sender_id (Union[Unset, str]):
        sender_name (Union[Unset, str]):
        override_username (Union[Unset, str]):
        override_icon_url (Union[Unset, str]):
        from_webhook (Union[Unset, str]):
        version (Union[Unset, str]):
        is_id_loaded (Union[Unset, bool]):
    """

    ack_id: Union[Unset, str] = UNSET
    platform: Union[Unset, str] = UNSET
    server_id: Union[Unset, str] = UNSET
    device_id: Union[Unset, str] = UNSET
    post_id: Union[Unset, str] = UNSET
    category: Union[Unset, str] = UNSET
    sound: Union[Unset, str] = UNSET
    message: Union[Unset, str] = UNSET
    badge: Union[Unset, float] = UNSET
    cont_ava: Union[Unset, float] = UNSET
    team_id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    root_id: Union[Unset, str] = UNSET
    channel_name: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    sender_id: Union[Unset, str] = UNSET
    sender_name: Union[Unset, str] = UNSET
    override_username: Union[Unset, str] = UNSET
    override_icon_url: Union[Unset, str] = UNSET
    from_webhook: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    is_id_loaded: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ack_id = self.ack_id

        platform = self.platform

        server_id = self.server_id

        device_id = self.device_id

        post_id = self.post_id

        category = self.category

        sound = self.sound

        message = self.message

        badge = self.badge

        cont_ava = self.cont_ava

        team_id = self.team_id

        channel_id = self.channel_id

        root_id = self.root_id

        channel_name = self.channel_name

        type_ = self.type_

        sender_id = self.sender_id

        sender_name = self.sender_name

        override_username = self.override_username

        override_icon_url = self.override_icon_url

        from_webhook = self.from_webhook

        version = self.version

        is_id_loaded = self.is_id_loaded

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ack_id is not UNSET:
            field_dict["ack_id"] = ack_id
        if platform is not UNSET:
            field_dict["platform"] = platform
        if server_id is not UNSET:
            field_dict["server_id"] = server_id
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if post_id is not UNSET:
            field_dict["post_id"] = post_id
        if category is not UNSET:
            field_dict["category"] = category
        if sound is not UNSET:
            field_dict["sound"] = sound
        if message is not UNSET:
            field_dict["message"] = message
        if badge is not UNSET:
            field_dict["badge"] = badge
        if cont_ava is not UNSET:
            field_dict["cont_ava"] = cont_ava
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if root_id is not UNSET:
            field_dict["root_id"] = root_id
        if channel_name is not UNSET:
            field_dict["channel_name"] = channel_name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if sender_id is not UNSET:
            field_dict["sender_id"] = sender_id
        if sender_name is not UNSET:
            field_dict["sender_name"] = sender_name
        if override_username is not UNSET:
            field_dict["override_username"] = override_username
        if override_icon_url is not UNSET:
            field_dict["override_icon_url"] = override_icon_url
        if from_webhook is not UNSET:
            field_dict["from_webhook"] = from_webhook
        if version is not UNSET:
            field_dict["version"] = version
        if is_id_loaded is not UNSET:
            field_dict["is_id_loaded"] = is_id_loaded

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ack_id = d.pop("ack_id", UNSET)

        platform = d.pop("platform", UNSET)

        server_id = d.pop("server_id", UNSET)

        device_id = d.pop("device_id", UNSET)

        post_id = d.pop("post_id", UNSET)

        category = d.pop("category", UNSET)

        sound = d.pop("sound", UNSET)

        message = d.pop("message", UNSET)

        badge = d.pop("badge", UNSET)

        cont_ava = d.pop("cont_ava", UNSET)

        team_id = d.pop("team_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        root_id = d.pop("root_id", UNSET)

        channel_name = d.pop("channel_name", UNSET)

        type_ = d.pop("type", UNSET)

        sender_id = d.pop("sender_id", UNSET)

        sender_name = d.pop("sender_name", UNSET)

        override_username = d.pop("override_username", UNSET)

        override_icon_url = d.pop("override_icon_url", UNSET)

        from_webhook = d.pop("from_webhook", UNSET)

        version = d.pop("version", UNSET)

        is_id_loaded = d.pop("is_id_loaded", UNSET)

        push_notification = cls(
            ack_id=ack_id,
            platform=platform,
            server_id=server_id,
            device_id=device_id,
            post_id=post_id,
            category=category,
            sound=sound,
            message=message,
            badge=badge,
            cont_ava=cont_ava,
            team_id=team_id,
            channel_id=channel_id,
            root_id=root_id,
            channel_name=channel_name,
            type_=type_,
            sender_id=sender_id,
            sender_name=sender_name,
            override_username=override_username,
            override_icon_url=override_icon_url,
            from_webhook=from_webhook,
            version=version,
            is_id_loaded=is_id_loaded,
        )

        push_notification.additional_properties = d
        return push_notification

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
