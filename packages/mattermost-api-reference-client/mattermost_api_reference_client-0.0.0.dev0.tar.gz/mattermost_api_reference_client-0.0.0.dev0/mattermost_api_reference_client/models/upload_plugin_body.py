from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="UploadPluginBody")


@_attrs_define
class UploadPluginBody:
    """
    Attributes:
        plugin (File): The plugin image to be uploaded
        force (Union[Unset, str]): Set to 'true' to overwrite a previously installed plugin with the same ID, if any
    """

    plugin: File
    force: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plugin = self.plugin.to_tuple()

        force = self.force

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plugin": plugin,
            }
        )
        if force is not UNSET:
            field_dict["force"] = force

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("plugin", self.plugin.to_tuple()))

        if not isinstance(self.force, Unset):
            files.append(("force", (None, str(self.force).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        plugin = File(payload=BytesIO(d.pop("plugin")))

        force = d.pop("force", UNSET)

        upload_plugin_body = cls(
            plugin=plugin,
            force=force,
        )

        upload_plugin_body.additional_properties = d
        return upload_plugin_body

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
