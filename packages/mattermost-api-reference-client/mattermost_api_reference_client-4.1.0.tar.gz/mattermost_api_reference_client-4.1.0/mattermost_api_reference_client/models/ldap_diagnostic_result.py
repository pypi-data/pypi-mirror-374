from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ldap_diagnostic_result_sample_results_item import LdapDiagnosticResultSampleResultsItem


T = TypeVar("T", bound="LdapDiagnosticResult")


@_attrs_define
class LdapDiagnosticResult:
    """
    Attributes:
        test_name (Union[Unset, str]): Name/type of the diagnostic test being performed
        test_value (Union[Unset, str]): The actual test value (filter string or attribute name)
        total_count (Union[Unset, int]): Number of entries found by the filter
        message (Union[Unset, str]): Optional success/info message
        error (Union[Unset, str]): Optional error message if test failed
        sample_results (Union[Unset, list['LdapDiagnosticResultSampleResultsItem']]): Array of sample LDAP entries found
    """

    test_name: Union[Unset, str] = UNSET
    test_value: Union[Unset, str] = UNSET
    total_count: Union[Unset, int] = UNSET
    message: Union[Unset, str] = UNSET
    error: Union[Unset, str] = UNSET
    sample_results: Union[Unset, list["LdapDiagnosticResultSampleResultsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        test_name = self.test_name

        test_value = self.test_value

        total_count = self.total_count

        message = self.message

        error = self.error

        sample_results: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sample_results, Unset):
            sample_results = []
            for sample_results_item_data in self.sample_results:
                sample_results_item = sample_results_item_data.to_dict()
                sample_results.append(sample_results_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if test_name is not UNSET:
            field_dict["test_name"] = test_name
        if test_value is not UNSET:
            field_dict["test_value"] = test_value
        if total_count is not UNSET:
            field_dict["total_count"] = total_count
        if message is not UNSET:
            field_dict["message"] = message
        if error is not UNSET:
            field_dict["error"] = error
        if sample_results is not UNSET:
            field_dict["sample_results"] = sample_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ldap_diagnostic_result_sample_results_item import LdapDiagnosticResultSampleResultsItem

        d = dict(src_dict)
        test_name = d.pop("test_name", UNSET)

        test_value = d.pop("test_value", UNSET)

        total_count = d.pop("total_count", UNSET)

        message = d.pop("message", UNSET)

        error = d.pop("error", UNSET)

        sample_results = []
        _sample_results = d.pop("sample_results", UNSET)
        for sample_results_item_data in _sample_results or []:
            sample_results_item = LdapDiagnosticResultSampleResultsItem.from_dict(sample_results_item_data)

            sample_results.append(sample_results_item)

        ldap_diagnostic_result = cls(
            test_name=test_name,
            test_value=test_value,
            total_count=total_count,
            message=message,
            error=error,
            sample_results=sample_results,
        )

        ldap_diagnostic_result.additional_properties = d
        return ldap_diagnostic_result

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
