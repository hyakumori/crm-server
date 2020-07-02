from uuid import uuid4

import pytest
from django.utils.translation import gettext_lazy as _
from rest_framework.test import force_authenticate

from hyakumori_crm.crm.models import (
    Customer,
    CustomerContact,
    Contact,
    ForestCustomer,
)
from hyakumori_crm.crm.schemas.contract import (
    ContractType,
    ContractTypeStatus,
    FSCContactStatus,
)
from hyakumori_crm.forest.restful import (
    update_owners_view,
    ForestViewSets,
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
        f"/api/v1/forests/{forest.pk}/basic-info",
        {
            "cadastral": {"prefecture": "foo", "municipality": "foo", "sector": "bar"},
            "contracts": {
                "contact_type": ContractType.long_term.value,
                "contact_status": ContractTypeStatus.negotiated,
                "contact_start_date": "2020-05-20",
                "contact_end_date": "2022-05-20",
                "fsc_start_date": "2020-05-20",
                "fsc_status": FSCContactStatus.joined,
            },
            "land_attributes": {"地番本番": "10", "地番支番": None},
        },
        format="json",
    )
    view = ForestViewSets.as_view({"put": "basic_info"})
    force_authenticate(req, user=admin_user)
    resp = view(req, pk=forest.pk)
    assert resp.status_code == 200
    forest.refresh_from_db()
    assert forest.cadastral["sector"] == "bar"


@pytest.mark.django_db
def test_update_forest_basic_info_not_found(api_rf, admin_user):
    pk = uuid4()
    req = api_rf.put(f"/api/v1/forests/{pk}/basic-info", {}, format="json",)
    view = ForestViewSets.as_view({"put": "basic_info"})
    force_authenticate(req, user=admin_user)
    resp = view(req, pk=pk)
    assert resp.status_code == 404
    assert resp.render().data["detail"] == _("Forest not found")


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
    ForestCustomer.objects.create(forest=forest, customer=customer1)

    req = api_rf.put(
        f"/api/v1/forests/{forest.pk}/customers",
        {"added": [customer2.pk], "deleted": []},
        format="json",
    )
    force_authenticate(req, user=admin_user)
    resp = update_owners_view(req, pk=forest.pk)
    forest.refresh_from_db()
    assert resp.status_code == 200
    assert ForestCustomer.objects.count() == 2
