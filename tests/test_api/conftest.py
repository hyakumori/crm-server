import pytest
from rest_framework.test import APIRequestFactory
from hyakumori_crm.users.models import User


@pytest.fixture()
def api_rf():
    return APIRequestFactory()


@pytest.fixture()
def admin_user():
    return User.objects.create_superuser(
        email="admin@example.com", password="testp4sswrd"
    )
