from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.open_graph_article import OpenGraphArticle
    from ..models.open_graph_audios_item import OpenGraphAudiosItem
    from ..models.open_graph_book import OpenGraphBook
    from ..models.open_graph_images_item import OpenGraphImagesItem
    from ..models.open_graph_profile import OpenGraphProfile
    from ..models.open_graph_videos_item import OpenGraphVideosItem


T = TypeVar("T", bound="OpenGraph")


@_attrs_define
class OpenGraph:
    """OpenGraph metadata of a webpage

    Attributes:
        type_ (Union[Unset, str]):
        url (Union[Unset, str]):
        title (Union[Unset, str]):
        description (Union[Unset, str]):
        determiner (Union[Unset, str]):
        site_name (Union[Unset, str]):
        locale (Union[Unset, str]):
        locales_alternate (Union[Unset, list[str]]):
        images (Union[Unset, list['OpenGraphImagesItem']]):
        videos (Union[Unset, list['OpenGraphVideosItem']]):
        audios (Union[Unset, list['OpenGraphAudiosItem']]):
        article (Union[Unset, OpenGraphArticle]): Article object used in OpenGraph metadata of a webpage, if type is
            article
        book (Union[Unset, OpenGraphBook]): Book object used in OpenGraph metadata of a webpage, if type is book
        profile (Union[Unset, OpenGraphProfile]):
    """

    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    determiner: Union[Unset, str] = UNSET
    site_name: Union[Unset, str] = UNSET
    locale: Union[Unset, str] = UNSET
    locales_alternate: Union[Unset, list[str]] = UNSET
    images: Union[Unset, list["OpenGraphImagesItem"]] = UNSET
    videos: Union[Unset, list["OpenGraphVideosItem"]] = UNSET
    audios: Union[Unset, list["OpenGraphAudiosItem"]] = UNSET
    article: Union[Unset, "OpenGraphArticle"] = UNSET
    book: Union[Unset, "OpenGraphBook"] = UNSET
    profile: Union[Unset, "OpenGraphProfile"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        url = self.url

        title = self.title

        description = self.description

        determiner = self.determiner

        site_name = self.site_name

        locale = self.locale

        locales_alternate: Union[Unset, list[str]] = UNSET
        if not isinstance(self.locales_alternate, Unset):
            locales_alternate = self.locales_alternate

        images: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.images, Unset):
            images = []
            for images_item_data in self.images:
                images_item = images_item_data.to_dict()
                images.append(images_item)

        videos: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.videos, Unset):
            videos = []
            for videos_item_data in self.videos:
                videos_item = videos_item_data.to_dict()
                videos.append(videos_item)

        audios: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.audios, Unset):
            audios = []
            for audios_item_data in self.audios:
                audios_item = audios_item_data.to_dict()
                audios.append(audios_item)

        article: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.article, Unset):
            article = self.article.to_dict()

        book: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.book, Unset):
            book = self.book.to_dict()

        profile: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.profile, Unset):
            profile = self.profile.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if determiner is not UNSET:
            field_dict["determiner"] = determiner
        if site_name is not UNSET:
            field_dict["site_name"] = site_name
        if locale is not UNSET:
            field_dict["locale"] = locale
        if locales_alternate is not UNSET:
            field_dict["locales_alternate"] = locales_alternate
        if images is not UNSET:
            field_dict["images"] = images
        if videos is not UNSET:
            field_dict["videos"] = videos
        if audios is not UNSET:
            field_dict["audios"] = audios
        if article is not UNSET:
            field_dict["article"] = article
        if book is not UNSET:
            field_dict["book"] = book
        if profile is not UNSET:
            field_dict["profile"] = profile

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_graph_article import OpenGraphArticle
        from ..models.open_graph_audios_item import OpenGraphAudiosItem
        from ..models.open_graph_book import OpenGraphBook
        from ..models.open_graph_images_item import OpenGraphImagesItem
        from ..models.open_graph_profile import OpenGraphProfile
        from ..models.open_graph_videos_item import OpenGraphVideosItem

        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        title = d.pop("title", UNSET)

        description = d.pop("description", UNSET)

        determiner = d.pop("determiner", UNSET)

        site_name = d.pop("site_name", UNSET)

        locale = d.pop("locale", UNSET)

        locales_alternate = cast(list[str], d.pop("locales_alternate", UNSET))

        images = []
        _images = d.pop("images", UNSET)
        for images_item_data in _images or []:
            images_item = OpenGraphImagesItem.from_dict(images_item_data)

            images.append(images_item)

        videos = []
        _videos = d.pop("videos", UNSET)
        for videos_item_data in _videos or []:
            videos_item = OpenGraphVideosItem.from_dict(videos_item_data)

            videos.append(videos_item)

        audios = []
        _audios = d.pop("audios", UNSET)
        for audios_item_data in _audios or []:
            audios_item = OpenGraphAudiosItem.from_dict(audios_item_data)

            audios.append(audios_item)

        _article = d.pop("article", UNSET)
        article: Union[Unset, OpenGraphArticle]
        if isinstance(_article, Unset):
            article = UNSET
        else:
            article = OpenGraphArticle.from_dict(_article)

        _book = d.pop("book", UNSET)
        book: Union[Unset, OpenGraphBook]
        if isinstance(_book, Unset):
            book = UNSET
        else:
            book = OpenGraphBook.from_dict(_book)

        _profile = d.pop("profile", UNSET)
        profile: Union[Unset, OpenGraphProfile]
        if isinstance(_profile, Unset):
            profile = UNSET
        else:
            profile = OpenGraphProfile.from_dict(_profile)

        open_graph = cls(
            type_=type_,
            url=url,
            title=title,
            description=description,
            determiner=determiner,
            site_name=site_name,
            locale=locale,
            locales_alternate=locales_alternate,
            images=images,
            videos=videos,
            audios=audios,
            article=article,
            book=book,
            profile=profile,
        )

        open_graph.additional_properties = d
        return open_graph

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
