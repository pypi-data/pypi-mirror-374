from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigFileSettings")


@_attrs_define
class ConfigFileSettings:
    """
    Attributes:
        max_file_size (Union[Unset, int]):
        driver_name (Union[Unset, str]):
        directory (Union[Unset, str]):
        enable_public_link (Union[Unset, bool]):
        public_link_salt (Union[Unset, str]):
        thumbnail_width (Union[Unset, int]):
        thumbnail_height (Union[Unset, int]):
        preview_width (Union[Unset, int]):
        preview_height (Union[Unset, int]):
        profile_width (Union[Unset, int]):
        profile_height (Union[Unset, int]):
        initial_font (Union[Unset, str]):
        amazon_s3_access_key_id (Union[Unset, str]):
        amazon_s3_secret_access_key (Union[Unset, str]):
        amazon_s3_bucket (Union[Unset, str]):
        amazon_s3_region (Union[Unset, str]):
        amazon_s3_endpoint (Union[Unset, str]):
        amazon_s3ssl (Union[Unset, bool]):
        amazon_s3_storage_class (Union[Unset, str]):
    """

    max_file_size: Union[Unset, int] = UNSET
    driver_name: Union[Unset, str] = UNSET
    directory: Union[Unset, str] = UNSET
    enable_public_link: Union[Unset, bool] = UNSET
    public_link_salt: Union[Unset, str] = UNSET
    thumbnail_width: Union[Unset, int] = UNSET
    thumbnail_height: Union[Unset, int] = UNSET
    preview_width: Union[Unset, int] = UNSET
    preview_height: Union[Unset, int] = UNSET
    profile_width: Union[Unset, int] = UNSET
    profile_height: Union[Unset, int] = UNSET
    initial_font: Union[Unset, str] = UNSET
    amazon_s3_access_key_id: Union[Unset, str] = UNSET
    amazon_s3_secret_access_key: Union[Unset, str] = UNSET
    amazon_s3_bucket: Union[Unset, str] = UNSET
    amazon_s3_region: Union[Unset, str] = UNSET
    amazon_s3_endpoint: Union[Unset, str] = UNSET
    amazon_s3ssl: Union[Unset, bool] = UNSET
    amazon_s3_storage_class: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_file_size = self.max_file_size

        driver_name = self.driver_name

        directory = self.directory

        enable_public_link = self.enable_public_link

        public_link_salt = self.public_link_salt

        thumbnail_width = self.thumbnail_width

        thumbnail_height = self.thumbnail_height

        preview_width = self.preview_width

        preview_height = self.preview_height

        profile_width = self.profile_width

        profile_height = self.profile_height

        initial_font = self.initial_font

        amazon_s3_access_key_id = self.amazon_s3_access_key_id

        amazon_s3_secret_access_key = self.amazon_s3_secret_access_key

        amazon_s3_bucket = self.amazon_s3_bucket

        amazon_s3_region = self.amazon_s3_region

        amazon_s3_endpoint = self.amazon_s3_endpoint

        amazon_s3ssl = self.amazon_s3ssl

        amazon_s3_storage_class = self.amazon_s3_storage_class

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_file_size is not UNSET:
            field_dict["MaxFileSize"] = max_file_size
        if driver_name is not UNSET:
            field_dict["DriverName"] = driver_name
        if directory is not UNSET:
            field_dict["Directory"] = directory
        if enable_public_link is not UNSET:
            field_dict["EnablePublicLink"] = enable_public_link
        if public_link_salt is not UNSET:
            field_dict["PublicLinkSalt"] = public_link_salt
        if thumbnail_width is not UNSET:
            field_dict["ThumbnailWidth"] = thumbnail_width
        if thumbnail_height is not UNSET:
            field_dict["ThumbnailHeight"] = thumbnail_height
        if preview_width is not UNSET:
            field_dict["PreviewWidth"] = preview_width
        if preview_height is not UNSET:
            field_dict["PreviewHeight"] = preview_height
        if profile_width is not UNSET:
            field_dict["ProfileWidth"] = profile_width
        if profile_height is not UNSET:
            field_dict["ProfileHeight"] = profile_height
        if initial_font is not UNSET:
            field_dict["InitialFont"] = initial_font
        if amazon_s3_access_key_id is not UNSET:
            field_dict["AmazonS3AccessKeyId"] = amazon_s3_access_key_id
        if amazon_s3_secret_access_key is not UNSET:
            field_dict["AmazonS3SecretAccessKey"] = amazon_s3_secret_access_key
        if amazon_s3_bucket is not UNSET:
            field_dict["AmazonS3Bucket"] = amazon_s3_bucket
        if amazon_s3_region is not UNSET:
            field_dict["AmazonS3Region"] = amazon_s3_region
        if amazon_s3_endpoint is not UNSET:
            field_dict["AmazonS3Endpoint"] = amazon_s3_endpoint
        if amazon_s3ssl is not UNSET:
            field_dict["AmazonS3SSL"] = amazon_s3ssl
        if amazon_s3_storage_class is not UNSET:
            field_dict["AmazonS3StorageClass"] = amazon_s3_storage_class

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_file_size = d.pop("MaxFileSize", UNSET)

        driver_name = d.pop("DriverName", UNSET)

        directory = d.pop("Directory", UNSET)

        enable_public_link = d.pop("EnablePublicLink", UNSET)

        public_link_salt = d.pop("PublicLinkSalt", UNSET)

        thumbnail_width = d.pop("ThumbnailWidth", UNSET)

        thumbnail_height = d.pop("ThumbnailHeight", UNSET)

        preview_width = d.pop("PreviewWidth", UNSET)

        preview_height = d.pop("PreviewHeight", UNSET)

        profile_width = d.pop("ProfileWidth", UNSET)

        profile_height = d.pop("ProfileHeight", UNSET)

        initial_font = d.pop("InitialFont", UNSET)

        amazon_s3_access_key_id = d.pop("AmazonS3AccessKeyId", UNSET)

        amazon_s3_secret_access_key = d.pop("AmazonS3SecretAccessKey", UNSET)

        amazon_s3_bucket = d.pop("AmazonS3Bucket", UNSET)

        amazon_s3_region = d.pop("AmazonS3Region", UNSET)

        amazon_s3_endpoint = d.pop("AmazonS3Endpoint", UNSET)

        amazon_s3ssl = d.pop("AmazonS3SSL", UNSET)

        amazon_s3_storage_class = d.pop("AmazonS3StorageClass", UNSET)

        config_file_settings = cls(
            max_file_size=max_file_size,
            driver_name=driver_name,
            directory=directory,
            enable_public_link=enable_public_link,
            public_link_salt=public_link_salt,
            thumbnail_width=thumbnail_width,
            thumbnail_height=thumbnail_height,
            preview_width=preview_width,
            preview_height=preview_height,
            profile_width=profile_width,
            profile_height=profile_height,
            initial_font=initial_font,
            amazon_s3_access_key_id=amazon_s3_access_key_id,
            amazon_s3_secret_access_key=amazon_s3_secret_access_key,
            amazon_s3_bucket=amazon_s3_bucket,
            amazon_s3_region=amazon_s3_region,
            amazon_s3_endpoint=amazon_s3_endpoint,
            amazon_s3ssl=amazon_s3ssl,
            amazon_s3_storage_class=amazon_s3_storage_class,
        )

        config_file_settings.additional_properties = d
        return config_file_settings

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
