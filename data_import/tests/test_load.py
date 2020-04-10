import os
import pickle
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from dotenv import load_dotenv

from data_import.lib.utils import prepare_env
from data_import.services.customer import CustomerService

load_dotenv(Path(__file__).parent.parent.joinpath(".env"))

EXCEL_FILE_PATH = Path(os.getenv("ORIGINAL_XLSX_PATH"))
MASTER_DATA_PATH = EXCEL_FILE_PATH.parent.joinpath("master-data.pickle")

prepare_env()


class SimpleLoadTestCase(TestCase):
    def setUp(self):
        try:
            self.data = pickle.load(open(MASTER_DATA_PATH, "rb"))
        except OSError:
            self.data = None

        self.user = get_user_model().objects.create_user(
            email="test@test.dev", password="TeSt.PassWord!"
        )

    def test_insert_record(self):
        if self.data is None:
            print(f"Skipped {self.id()} due to no data found")
            return

        customer = CustomerService.create_customer(self.data["customer"]["2001705"], self.user)

        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.customercontact_set.count(), 1)
        self.assertEqual(customer.customercontact_set.filter(is_basic=True).first().contact.postal_code, "679-5322")

        CustomerService.delete_customer_by_id(customer.id)
        customer.refresh_from_db()

        self.assertTrue(customer.is_deleted)
