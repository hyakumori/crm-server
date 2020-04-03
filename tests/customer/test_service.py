import pytest
from hyakumori_crm.customer.models import Customer, RELATIONSHIP_TYPE, Contact
from hyakumori_crm.customer.service import create, add_contacts, get_list


@pytest.mark.django_db
def test_create_customer():
    c = create(dict(profile={"first_name": "Foo", "last_name": "Bar"}))
    c.save()
    assert c.id is not None


@pytest.mark.django_db
def test_add_contact_to_customer():
    c = create(dict(profile={"first_name": "Foo", "last_name": "Bar"}))
    c.save()
    contacts = add_contacts(
        c,
        [
            dict(
                profile={"first_name": "FooFoo", "last_name": "Bar"},
                relationship_type=RELATIONSHIP_TYPE.SON,
            )
        ],
    )
    contact = contacts[0]
    assert (
        contact.customercontact_set.get(
            customer_id=c.id, contact_id=contact.id
        ).relationship_type
        == RELATIONSHIP_TYPE.SON
    )
    assert c.contacts.count() == 1

    contacts = add_contacts(
        c, [dict(profile={"first_name": "Yam", "last_name": "Bar"},)],
    )
    contact = contacts[0]
    assert (
        contact.customercontact_set.get(
            customer_id=c.id, contact_id=contact.id
        ).relationship_type
        == ""
    )
    assert c.contacts.count() == 2


@pytest.mark.django_db
def test_get_list():
    c = create(dict(profile={"first_name": "Foo", "last_name": "Bar"}))
    c.save()
    contacts = add_contacts(
        c,
        [
            dict(
                profile={"first_name": "FooFoo", "last_name": "Bar"},
                relationship_type=RELATIONSHIP_TYPE.SON,
            ),
            dict(profile={"first_name": "Yam", "last_name": "Bar"},),
        ],
    )

    customers, total = get_list()
    assert total == 1
    assert customers[0]["representative"] == "Bar Yam"
    assert customers[0]["fullname"] == "Bar Foo"
