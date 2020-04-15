from django.contrib.auth import get_user_model

from ..services.forest import ForestService
from .base import BaseDbImporter


class ForestDbImporter(BaseDbImporter):
    @staticmethod
    def insert_db(results: dict):
        # TODO: should we provide way to customize this?
        processed_count = 0
        total = len(results.keys())
        batch = int(total / 50)

        for _, forest in results.items():
            ForestService.create_forest(forest)

            if processed_count % batch == 0:
                print(
                    "progress: {percent}%".format(
                        percent=int(processed_count * 100 / total)
                    ),
                    flush=True,
                )

            processed_count += 1

    @staticmethod
    def create_relation_customer(results: dict):
        for _, forest in results.items():
            ForestService.create_forest_customer_relation(forest)
