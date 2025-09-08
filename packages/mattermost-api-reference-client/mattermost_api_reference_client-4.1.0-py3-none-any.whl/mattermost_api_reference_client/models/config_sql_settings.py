from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigSqlSettings")


@_attrs_define
class ConfigSqlSettings:
    """
    Attributes:
        driver_name (Union[Unset, str]):
        data_source (Union[Unset, str]):
        data_source_replicas (Union[Unset, list[str]]):
        max_idle_conns (Union[Unset, int]):
        max_open_conns (Union[Unset, int]):
        trace (Union[Unset, bool]):
        at_rest_encrypt_key (Union[Unset, str]):
    """

    driver_name: Union[Unset, str] = UNSET
    data_source: Union[Unset, str] = UNSET
    data_source_replicas: Union[Unset, list[str]] = UNSET
    max_idle_conns: Union[Unset, int] = UNSET
    max_open_conns: Union[Unset, int] = UNSET
    trace: Union[Unset, bool] = UNSET
    at_rest_encrypt_key: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        driver_name = self.driver_name

        data_source = self.data_source

        data_source_replicas: Union[Unset, list[str]] = UNSET
        if not isinstance(self.data_source_replicas, Unset):
            data_source_replicas = self.data_source_replicas

        max_idle_conns = self.max_idle_conns

        max_open_conns = self.max_open_conns

        trace = self.trace

        at_rest_encrypt_key = self.at_rest_encrypt_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if driver_name is not UNSET:
            field_dict["DriverName"] = driver_name
        if data_source is not UNSET:
            field_dict["DataSource"] = data_source
        if data_source_replicas is not UNSET:
            field_dict["DataSourceReplicas"] = data_source_replicas
        if max_idle_conns is not UNSET:
            field_dict["MaxIdleConns"] = max_idle_conns
        if max_open_conns is not UNSET:
            field_dict["MaxOpenConns"] = max_open_conns
        if trace is not UNSET:
            field_dict["Trace"] = trace
        if at_rest_encrypt_key is not UNSET:
            field_dict["AtRestEncryptKey"] = at_rest_encrypt_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        driver_name = d.pop("DriverName", UNSET)

        data_source = d.pop("DataSource", UNSET)

        data_source_replicas = cast(list[str], d.pop("DataSourceReplicas", UNSET))

        max_idle_conns = d.pop("MaxIdleConns", UNSET)

        max_open_conns = d.pop("MaxOpenConns", UNSET)

        trace = d.pop("Trace", UNSET)

        at_rest_encrypt_key = d.pop("AtRestEncryptKey", UNSET)

        config_sql_settings = cls(
            driver_name=driver_name,
            data_source=data_source,
            data_source_replicas=data_source_replicas,
            max_idle_conns=max_idle_conns,
            max_open_conns=max_open_conns,
            trace=trace,
            at_rest_encrypt_key=at_rest_encrypt_key,
        )

        config_sql_settings.additional_properties = d
        return config_sql_settings

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
