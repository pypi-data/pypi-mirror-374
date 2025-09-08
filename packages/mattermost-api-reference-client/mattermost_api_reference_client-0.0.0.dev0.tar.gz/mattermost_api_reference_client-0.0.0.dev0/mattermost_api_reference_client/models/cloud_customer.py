from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.address import Address
    from ..models.payment_method import PaymentMethod


T = TypeVar("T", bound="CloudCustomer")


@_attrs_define
class CloudCustomer:
    """
    Attributes:
        id (Union[Unset, str]):
        creator_id (Union[Unset, str]):
        create_at (Union[Unset, int]):
        email (Union[Unset, str]):
        name (Union[Unset, str]):
        num_employees (Union[Unset, str]):
        contact_first_name (Union[Unset, str]):
        contact_last_name (Union[Unset, str]):
        billing_address (Union[Unset, Address]):
        company_address (Union[Unset, Address]):
        payment_method (Union[Unset, PaymentMethod]):
    """

    id: Union[Unset, str] = UNSET
    creator_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    email: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    num_employees: Union[Unset, str] = UNSET
    contact_first_name: Union[Unset, str] = UNSET
    contact_last_name: Union[Unset, str] = UNSET
    billing_address: Union[Unset, "Address"] = UNSET
    company_address: Union[Unset, "Address"] = UNSET
    payment_method: Union[Unset, "PaymentMethod"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        creator_id = self.creator_id

        create_at = self.create_at

        email = self.email

        name = self.name

        num_employees = self.num_employees

        contact_first_name = self.contact_first_name

        contact_last_name = self.contact_last_name

        billing_address: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.billing_address, Unset):
            billing_address = self.billing_address.to_dict()

        company_address: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.company_address, Unset):
            company_address = self.company_address.to_dict()

        payment_method: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.payment_method, Unset):
            payment_method = self.payment_method.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if creator_id is not UNSET:
            field_dict["creator_id"] = creator_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if email is not UNSET:
            field_dict["email"] = email
        if name is not UNSET:
            field_dict["name"] = name
        if num_employees is not UNSET:
            field_dict["num_employees"] = num_employees
        if contact_first_name is not UNSET:
            field_dict["contact_first_name"] = contact_first_name
        if contact_last_name is not UNSET:
            field_dict["contact_last_name"] = contact_last_name
        if billing_address is not UNSET:
            field_dict["billing_address"] = billing_address
        if company_address is not UNSET:
            field_dict["company_address"] = company_address
        if payment_method is not UNSET:
            field_dict["payment_method"] = payment_method

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.address import Address
        from ..models.payment_method import PaymentMethod

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        creator_id = d.pop("creator_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        email = d.pop("email", UNSET)

        name = d.pop("name", UNSET)

        num_employees = d.pop("num_employees", UNSET)

        contact_first_name = d.pop("contact_first_name", UNSET)

        contact_last_name = d.pop("contact_last_name", UNSET)

        _billing_address = d.pop("billing_address", UNSET)
        billing_address: Union[Unset, Address]
        if isinstance(_billing_address, Unset):
            billing_address = UNSET
        else:
            billing_address = Address.from_dict(_billing_address)

        _company_address = d.pop("company_address", UNSET)
        company_address: Union[Unset, Address]
        if isinstance(_company_address, Unset):
            company_address = UNSET
        else:
            company_address = Address.from_dict(_company_address)

        _payment_method = d.pop("payment_method", UNSET)
        payment_method: Union[Unset, PaymentMethod]
        if isinstance(_payment_method, Unset):
            payment_method = UNSET
        else:
            payment_method = PaymentMethod.from_dict(_payment_method)

        cloud_customer = cls(
            id=id,
            creator_id=creator_id,
            create_at=create_at,
            email=email,
            name=name,
            num_employees=num_employees,
            contact_first_name=contact_first_name,
            contact_last_name=contact_last_name,
            billing_address=billing_address,
            company_address=company_address,
            payment_method=payment_method,
        )

        cloud_customer.additional_properties = d
        return cloud_customer

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
