from uuid import uuid4

import pytest
from rest_framework.test import force_authenticate

from hyakumori_crm.crm.models import (
    Forest,
    Customer,
    CustomerContact,
    Contact,
    ForestCustomer,
)
from hyakumori_crm.crm.schemas.contract import ContractType
from hyakumori_crm.forest.restful import (
    update,
    update_owners_view,
    set_contact_to_owner_view,
    ForestViewSets,
)


@pytest.fixture
def forest(admin_user):
    return Forest.objects.create(
        cadastral={"prefecture": "foo", "municipality": "foo", "sector": "foo"},
        contracts=[{"type": ContractType.long_term}],
    )


def test_get_customers_of_forest_unauthorize(api_rf):
    pk = uuid4()
    req = api_rf.get(f"/api/v1/forests/{pk}/customers")
    view = ForestViewSets.as_view({"get": "customers"})
    resp = view(req, pk=pk)
    assert resp.status_code == 401


@pytest.mark.django_db
def test_get_customers_of_forest(api_rf, admin_user):
    pk = uuid4()
    req = api_rf.get(f"/api/v1/forests/{pk}/customers")
    view = ForestViewSets.as_view({"get": "customers"})
    force_authenticate(req, user=admin_user)
    resp = view(req, pk=pk)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_update_forest_basic_info(api_rf, admin_user, forest):
    req = api_rf.put(
        f"/api/v1/forests/{forest.pk}",
        {
            "cadastral": {"prefecture": "foo", "municipality": "foo", "sector": "bar"},
            "contracts": [{"type": ContractType.long_term.value}],
        },
        format="json",
    )
    view = ForestViewSets.as_view({"put": "basic_info"})
    force_authenticate(req, user=admin_user)
    resp = view(req, pk=forest.pk)
    forest.refresh_from_db()
    assert forest.cadastral["sector"] == "bar"
    assert resp.status_code == 200


@pytest.mark.django_db
def test_update_owners_view(api_rf, admin_user, forest):
    customer1 = Customer()
    customer2 = Customer()
    Customer.objects.bulk_create([customer1, customer2])
    contact_customer1 = Contact(
        name_kanji=dict(first_name="foo", last_name="bar"),
        name_kana=dict(first_name="foo", last_name="bar"),
    )
    contact_customer2 = Contact(
        name_kanji=dict(first_name="yam", last_name="bar"),
        name_kana=dict(first_name="yam", last_name="bar"),
    )
    Contact.objects.bulk_create([contact_customer1, contact_customer2])
    CustomerContact.objects.create(
        customer=customer1, contact=contact_customer1, is_basic=True,
    )
    CustomerContact.objects.create(
        customer=customer2, contact=contact_customer2, is_basic=True,
    )
    ForestCustomer.objects.create(
        forest=forest, customer=customer1, contact=contact_customer1,
    )

    req = api_rf.put(
        f"/api/v1/forests/{forest.pk}/customers",
        {"forest_pk": str(forest.id), "added": [customer2.pk], "deleted": []},
        format="json",
    )
    force_authenticate(req, user=admin_user)
    resp = update_owners_view(req, pk=forest.pk)
    forest.refresh_from_db()
    assert resp.status_code == 200
    assert ForestCustomer.objects.count() == 2


@pytest.mark.django_db
def test_set_contact_to_owner_view(api_rf, admin_user, forest):
    customer1 = Customer()
    customer2 = Customer()
    Customer.objects.bulk_create([customer1, customer2])
    contact_customer1 = Contact(
        name_kanji=dict(first_name="foo", last_name="bar"),
        name_kana=dict(first_name="foo", last_name="bar"),
    )
    contact_customer2 = Contact(
        name_kanji=dict(first_name="yam", last_name="bar"),
        name_kana=dict(first_name="yam", last_name="bar"),
    )
    Contact.objects.bulk_create([contact_customer1, contact_customer2])
    CustomerContact.objects.create(
        customer=customer1, contact=contact_customer1, is_basic=True,
    )
    CustomerContact.objects.create(
        customer=customer2, contact=contact_customer2, is_basic=True,
    )
    ForestCustomer.objects.create(
        forest=forest, customer=customer1, contact=contact_customer1,
    )
    req = api_rf.put(
        f"/api/v1/forests/{forest.pk}/customers/set-contact",
        {
            "forest": str(forest.pk),
            "customer": str(customer1.pk),
            "contact": str(contact_customer2.pk),
        },
        format="json",
    )
    force_authenticate(req, user=admin_user)
    resp = set_contact_to_owner_view(req, pk=forest.pk)
    forest.refresh_from_db()
    assert resp.status_code == 200
    assert (
        ForestCustomer.objects.filter(
            forest=forest, customer=customer1, contact=contact_customer2,
        ).count()
        == 1
    )
    assert (
        ForestCustomer.objects.filter(
            forest=forest, customer=customer1, contact=contact_customer1,
        ).count()
        == 0
    )
