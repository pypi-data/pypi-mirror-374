from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.emoji import Emoji
    from ..models.file_info import FileInfo
    from ..models.post_acknowledgement import PostAcknowledgement
    from ..models.post_metadata_embeds_item import PostMetadataEmbedsItem
    from ..models.post_metadata_images import PostMetadataImages
    from ..models.post_metadata_priority import PostMetadataPriority
    from ..models.reaction import Reaction


T = TypeVar("T", bound="PostMetadata")


@_attrs_define
class PostMetadata:
    """Additional information used to display a post.

    Attributes:
        embeds (Union[Unset, list['PostMetadataEmbedsItem']]): Information about content embedded in the post including
            OpenGraph previews, image link previews, and message attachments. This field will be null if the post does not
            contain embedded content.
        emojis (Union[Unset, list['Emoji']]): The custom emojis that appear in this point or have been used in reactions
            to this post. This field will be null if the post does not contain custom emojis.
        files (Union[Unset, list['FileInfo']]): The FileInfo objects for any files attached to the post. This field will
            be null if the post does not have any file attachments.
        images (Union[Unset, PostMetadataImages]): An object mapping the URL of an external image to an object
            containing the dimensions of that image. This field will be null if the post or its embedded content does not
            reference any external images.
        reactions (Union[Unset, list['Reaction']]): Any reactions made to this point. This field will be null if no
            reactions have been made to this post.
        priority (Union[Unset, PostMetadataPriority]): Post priority set for this post. This field will be null if no
            priority metadata has been set.
        acknowledgements (Union[Unset, list['PostAcknowledgement']]): Any acknowledgements made to this point.
    """

    embeds: Union[Unset, list["PostMetadataEmbedsItem"]] = UNSET
    emojis: Union[Unset, list["Emoji"]] = UNSET
    files: Union[Unset, list["FileInfo"]] = UNSET
    images: Union[Unset, "PostMetadataImages"] = UNSET
    reactions: Union[Unset, list["Reaction"]] = UNSET
    priority: Union[Unset, "PostMetadataPriority"] = UNSET
    acknowledgements: Union[Unset, list["PostAcknowledgement"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        embeds: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.embeds, Unset):
            embeds = []
            for embeds_item_data in self.embeds:
                embeds_item = embeds_item_data.to_dict()
                embeds.append(embeds_item)

        emojis: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.emojis, Unset):
            emojis = []
            for emojis_item_data in self.emojis:
                emojis_item = emojis_item_data.to_dict()
                emojis.append(emojis_item)

        files: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.files, Unset):
            files = []
            for files_item_data in self.files:
                files_item = files_item_data.to_dict()
                files.append(files_item)

        images: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.images, Unset):
            images = self.images.to_dict()

        reactions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.reactions, Unset):
            reactions = []
            for reactions_item_data in self.reactions:
                reactions_item = reactions_item_data.to_dict()
                reactions.append(reactions_item)

        priority: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.priority, Unset):
            priority = self.priority.to_dict()

        acknowledgements: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.acknowledgements, Unset):
            acknowledgements = []
            for acknowledgements_item_data in self.acknowledgements:
                acknowledgements_item = acknowledgements_item_data.to_dict()
                acknowledgements.append(acknowledgements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if embeds is not UNSET:
            field_dict["embeds"] = embeds
        if emojis is not UNSET:
            field_dict["emojis"] = emojis
        if files is not UNSET:
            field_dict["files"] = files
        if images is not UNSET:
            field_dict["images"] = images
        if reactions is not UNSET:
            field_dict["reactions"] = reactions
        if priority is not UNSET:
            field_dict["priority"] = priority
        if acknowledgements is not UNSET:
            field_dict["acknowledgements"] = acknowledgements

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.emoji import Emoji
        from ..models.file_info import FileInfo
        from ..models.post_acknowledgement import PostAcknowledgement
        from ..models.post_metadata_embeds_item import PostMetadataEmbedsItem
        from ..models.post_metadata_images import PostMetadataImages
        from ..models.post_metadata_priority import PostMetadataPriority
        from ..models.reaction import Reaction

        d = dict(src_dict)
        embeds = []
        _embeds = d.pop("embeds", UNSET)
        for embeds_item_data in _embeds or []:
            embeds_item = PostMetadataEmbedsItem.from_dict(embeds_item_data)

            embeds.append(embeds_item)

        emojis = []
        _emojis = d.pop("emojis", UNSET)
        for emojis_item_data in _emojis or []:
            emojis_item = Emoji.from_dict(emojis_item_data)

            emojis.append(emojis_item)

        files = []
        _files = d.pop("files", UNSET)
        for files_item_data in _files or []:
            files_item = FileInfo.from_dict(files_item_data)

            files.append(files_item)

        _images = d.pop("images", UNSET)
        images: Union[Unset, PostMetadataImages]
        if isinstance(_images, Unset):
            images = UNSET
        else:
            images = PostMetadataImages.from_dict(_images)

        reactions = []
        _reactions = d.pop("reactions", UNSET)
        for reactions_item_data in _reactions or []:
            reactions_item = Reaction.from_dict(reactions_item_data)

            reactions.append(reactions_item)

        _priority = d.pop("priority", UNSET)
        priority: Union[Unset, PostMetadataPriority]
        if isinstance(_priority, Unset):
            priority = UNSET
        else:
            priority = PostMetadataPriority.from_dict(_priority)

        acknowledgements = []
        _acknowledgements = d.pop("acknowledgements", UNSET)
        for acknowledgements_item_data in _acknowledgements or []:
            acknowledgements_item = PostAcknowledgement.from_dict(acknowledgements_item_data)

            acknowledgements.append(acknowledgements_item)

        post_metadata = cls(
            embeds=embeds,
            emojis=emojis,
            files=files,
            images=images,
            reactions=reactions,
            priority=priority,
            acknowledgements=acknowledgements,
        )

        post_metadata.additional_properties = d
        return post_metadata

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
