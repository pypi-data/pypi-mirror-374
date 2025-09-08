from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.submit_performance_report_body_counters_item import SubmitPerformanceReportBodyCountersItem
    from ..models.submit_performance_report_body_histograms_item import SubmitPerformanceReportBodyHistogramsItem


T = TypeVar("T", bound="SubmitPerformanceReportBody")


@_attrs_define
class SubmitPerformanceReportBody:
    """
    Attributes:
        version (str): An identifier for the schema of the data being submitted which currently must be "0.1.0"
        start (int): The time in milliseconds of the first metric in this report
        end (int): The time in milliseconds of the last metric in this report
        client_id (Union[Unset, str]): Not currently used
        labels (Union[Unset, list[str]]): Labels to be applied to all metrics when recorded by the metrics backend
        counters (Union[Unset, list['SubmitPerformanceReportBodyCountersItem']]): An array of counter metrics to be
            reported
        histograms (Union[Unset, list['SubmitPerformanceReportBodyHistogramsItem']]): An array of histogram measurements
            to be reported
    """

    version: str
    start: int
    end: int
    client_id: Union[Unset, str] = UNSET
    labels: Union[Unset, list[str]] = UNSET
    counters: Union[Unset, list["SubmitPerformanceReportBodyCountersItem"]] = UNSET
    histograms: Union[Unset, list["SubmitPerformanceReportBodyHistogramsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        start = self.start

        end = self.end

        client_id = self.client_id

        labels: Union[Unset, list[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels

        counters: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.counters, Unset):
            counters = []
            for counters_item_data in self.counters:
                counters_item = counters_item_data.to_dict()
                counters.append(counters_item)

        histograms: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.histograms, Unset):
            histograms = []
            for histograms_item_data in self.histograms:
                histograms_item = histograms_item_data.to_dict()
                histograms.append(histograms_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "start": start,
                "end": end,
            }
        )
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if labels is not UNSET:
            field_dict["labels"] = labels
        if counters is not UNSET:
            field_dict["counters"] = counters
        if histograms is not UNSET:
            field_dict["histograms"] = histograms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.submit_performance_report_body_counters_item import SubmitPerformanceReportBodyCountersItem
        from ..models.submit_performance_report_body_histograms_item import SubmitPerformanceReportBodyHistogramsItem

        d = dict(src_dict)
        version = d.pop("version")

        start = d.pop("start")

        end = d.pop("end")

        client_id = d.pop("client_id", UNSET)

        labels = cast(list[str], d.pop("labels", UNSET))

        counters = []
        _counters = d.pop("counters", UNSET)
        for counters_item_data in _counters or []:
            counters_item = SubmitPerformanceReportBodyCountersItem.from_dict(counters_item_data)

            counters.append(counters_item)

        histograms = []
        _histograms = d.pop("histograms", UNSET)
        for histograms_item_data in _histograms or []:
            histograms_item = SubmitPerformanceReportBodyHistogramsItem.from_dict(histograms_item_data)

            histograms.append(histograms_item)

        submit_performance_report_body = cls(
            version=version,
            start=start,
            end=end,
            client_id=client_id,
            labels=labels,
            counters=counters,
            histograms=histograms,
        )

        submit_performance_report_body.additional_properties = d
        return submit_performance_report_body

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
