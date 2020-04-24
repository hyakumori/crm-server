import pytest
import orjson
from rest_framework.test import force_authenticate
from hyakumori_crm.crm.models import (
    Customer,
    CustomerContact,
    ForestCustomer,
    Contact,
    Forest,
    ForestCustomerContact,
)
from hyakumori_crm.crm.schemas.contract import ContractType
from hyakumori_crm.customer.restful import CustomerViewSets


def prepare_data():
    # create customers and contacts and customer-contact relations
    customer1 = Customer(internal_id="abcd111")
    customer2 = Customer(internal_id="abcd112")
    Customer.objects.bulk_create([customer1, customer2])
    self_contact1 = Contact(
        name_kanji=dict(last_name="foo", first_name="foo"),
        name_kana=dict(last_name="foo", first_name="foo"),
    )
    self_contact2 = Contact(
        name_kanji=dict(last_name="bar", first_name="bar"),
        name_kana=dict(last_name="bar", first_name="bar"),
    )
    contact3 = Contact(
        name_kanji=dict(last_name="coco", first_name="coco"),
        name_kana=dict(last_name="coco", first_name="coco"),
    )
    Contact.objects.bulk_create([self_contact1, self_contact2, contact3])
    contact_rel1 = CustomerContact(
        customer=customer1, contact=self_contact1, is_basic=True
    )
    contact_rel1_to_2 = CustomerContact(customer=customer1, contact=self_contact2)
    contact_rel1_to_3 = CustomerContact(customer=customer1, contact=contact3)
    contact_rel2 = CustomerContact(
        customer=customer2, contact=self_contact2, is_basic=True
    )
    CustomerContact.objects.bulk_create(
        [contact_rel1, contact_rel1_to_2, contact_rel2, contact_rel1_to_3]
    )

    # create forests
    forest1 = Forest(
        cadastral={"prefecture": "beep", "municipality": "yam", "sector": "jam"},
        contracts=[{"type": ContractType.long_term}],
    )
    forest2 = Forest(
        cadastral={"prefecture": "beep", "municipality": "beep", "sector": "beep"},
        contracts=[{"type": ContractType.long_term}],
    )
    Forest.objects.bulk_create([forest1, forest2])

    # create forest-customer relations
    customer1_rel1 = ForestCustomer(forest=forest1, customer=customer1)
    customer1_rel2 = ForestCustomer(forest=forest2, customer=customer1)
    customer2_rel1 = ForestCustomer(forest=forest1, customer=customer2)
    ForestCustomer.objects.bulk_create([customer1_rel1, customer1_rel2, customer2_rel1])
    ForestCustomerContact(
        customercontact_id=contact_rel1_to_2.id, forestcustomer_id=customer1_rel2.id
    ).save()
    return (
        customer1,
        customer2,
        self_contact1,
        self_contact2,
        contact3,
        forest1,
        forest2,
    )


@pytest.mark.django_db
def test_customer_contacts(admin_user, api_rf):
    (
        customer1,
        customer2,
        self_contact1,
        self_contact2,
        contact3,
        forest1,
        forest2,
    ) = prepare_data()
    req = api_rf.get(f"/api/v1/customers/{customer1.pk}/contacts")
    view = CustomerViewSets.as_view({"get": "contacts"})
    force_authenticate(req, user=admin_user)
    resp = view(req, pk=customer1.pk)
    resp.render()
    assert resp.status_code == 200
    resp_data = orjson.loads(resp.content)
    assert resp_data["count"] == 2
    assert len(resp_data["results"]) == 2
    # check forest1's contact is customer2's contact
    assert resp_data["results"][0]["id"] == str(self_contact2.id)
    # check customer2's contact has forest2
    assert resp_data["results"][0]["forest_id"] == str(forest2.id)

    assert resp_data["results"][1]["id"] == str(contact3.id)
    # check customer2's contact has forest2
    assert resp_data["results"][1]["forest_id"] is None


@pytest.mark.django_db
def test_customer_forests(admin_user, api_rf):
    (
        customer1,
        customer2,
        self_contact1,
        self_contact2,
        contact3,
        forest1,
        forest2,
    ) = prepare_data()

    req = api_rf.get(f"/api/v1/customers/{customer1.pk}/forests")
    view = CustomerViewSets.as_view({"get": "forests"})
    force_authenticate(req, user=admin_user)
    resp = view(req, pk=customer1.pk)
    resp.render()
    assert resp.status_code == 200
    resp_data = orjson.loads(resp.content)
    assert resp_data["count"] == 2
    assert len(resp_data["results"]) == 2

    assert resp_data["results"][0]["id"] == str(forest1.id)
    assert resp_data["results"][0]["customers_count"] == 2

    assert resp_data["results"][1]["id"] == str(forest2.id)
    assert resp_data["results"][1]["customers_count"] == 1
