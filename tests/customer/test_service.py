import pytest
from hyakumori_crm.crm.models.customer import Customer, Contact
from hyakumori_crm.customer.service import create, get_list
from hyakumori_crm.customer.schemas import CustomerInputSchema
from hyakumori_crm.users.models import User


@pytest.fixture
def customer_input():
    return CustomerInputSchema(
        basic_contact={
            "name_kana": {"first_name": "Foo", "last_name": "Bar"},
            "name_kanji": {"first_name": "Foo", "last_name": "Bar"},
            "postal_code": "123-4567",
        }
    )


@pytest.fixture
def admin_user():
    u = User.objects.create_superuser("example@foo.com", "example")
    return u


@pytest.mark.django_db
def test_create_customer(customer_input, admin_user):
    c = create(customer_in=customer_input)
    c.save()
    assert c.id is not None


@pytest.mark.django_db
def test_get_list(customer_input, admin_user):
    c = create(customer_in=customer_input)
    c.save()

    customers, total = get_list()
    assert total == 1
    assert customers[0]["fullname_kana"] == "Bar\u3000Foo"
