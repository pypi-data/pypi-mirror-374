from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_descriptor import MessageDescriptor


T = TypeVar("T", bound="PreviewModalContentData")


@_attrs_define
class PreviewModalContentData:
    """
    Attributes:
        sku_label (Union[Unset, MessageDescriptor]):
        title (Union[Unset, MessageDescriptor]):
        subtitle (Union[Unset, MessageDescriptor]):
        video_url (Union[Unset, str]): URL of the video content
        video_poster (Union[Unset, str]): URL of the video poster/thumbnail image
        use_case (Union[Unset, str]): The use case category for this content
    """

    sku_label: Union[Unset, "MessageDescriptor"] = UNSET
    title: Union[Unset, "MessageDescriptor"] = UNSET
    subtitle: Union[Unset, "MessageDescriptor"] = UNSET
    video_url: Union[Unset, str] = UNSET
    video_poster: Union[Unset, str] = UNSET
    use_case: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sku_label: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sku_label, Unset):
            sku_label = self.sku_label.to_dict()

        title: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.title, Unset):
            title = self.title.to_dict()

        subtitle: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.subtitle, Unset):
            subtitle = self.subtitle.to_dict()

        video_url = self.video_url

        video_poster = self.video_poster

        use_case = self.use_case

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sku_label is not UNSET:
            field_dict["skuLabel"] = sku_label
        if title is not UNSET:
            field_dict["title"] = title
        if subtitle is not UNSET:
            field_dict["subtitle"] = subtitle
        if video_url is not UNSET:
            field_dict["videoUrl"] = video_url
        if video_poster is not UNSET:
            field_dict["videoPoster"] = video_poster
        if use_case is not UNSET:
            field_dict["useCase"] = use_case

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_descriptor import MessageDescriptor

        d = dict(src_dict)
        _sku_label = d.pop("skuLabel", UNSET)
        sku_label: Union[Unset, MessageDescriptor]
        if isinstance(_sku_label, Unset):
            sku_label = UNSET
        else:
            sku_label = MessageDescriptor.from_dict(_sku_label)

        _title = d.pop("title", UNSET)
        title: Union[Unset, MessageDescriptor]
        if isinstance(_title, Unset):
            title = UNSET
        else:
            title = MessageDescriptor.from_dict(_title)

        _subtitle = d.pop("subtitle", UNSET)
        subtitle: Union[Unset, MessageDescriptor]
        if isinstance(_subtitle, Unset):
            subtitle = UNSET
        else:
            subtitle = MessageDescriptor.from_dict(_subtitle)

        video_url = d.pop("videoUrl", UNSET)

        video_poster = d.pop("videoPoster", UNSET)

        use_case = d.pop("useCase", UNSET)

        preview_modal_content_data = cls(
            sku_label=sku_label,
            title=title,
            subtitle=subtitle,
            video_url=video_url,
            video_poster=video_poster,
            use_case=use_case,
        )

        preview_modal_content_data.additional_properties = d
        return preview_modal_content_data

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
