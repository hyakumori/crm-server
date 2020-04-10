from django.contrib.auth import get_user_model

from ..services.customer import CustomerService
from .base import BaseDbImporter


class CustomerDbImporter(BaseDbImporter):
    @staticmethod
    def insert_db(results: dict):
        user = get_user_model().objects.first()
        processed_count = 0
        total = len(results.keys())
        batch = int(total / 50)

        for _, customer in results.items():
            CustomerService.create_customer(customer, user)

            if processed_count % batch == 0:
                print(
                    "progress: {percent}%".format(
                        percent=int(processed_count * 100 / total)
                    ),
                    flush=True,
                )

            processed_count += 1
