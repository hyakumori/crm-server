import pickle
from pathlib import Path
from uuid import uuid4

from django.contrib.auth import get_user_model
from hyakumori_crm.crm.schemas.customer import Banking, CustomerSchema

from ..lib.utils import parse_name_extra
from ..services.customer import CustomerService
from ..services.forest import ForestService
from .base import BaseDbImporter


class RelationDbImporter(BaseDbImporter):
    def __init__(self, master_data):
        self.forests = master_data.get("forest")
        self.customers = master_data.get("customer")
        self.dump_file = Path(__file__).parent.joinpath("forest_customer_link.pickle")
        self.user = get_user_model().objects.first()

    def _create_dump(self, data):
        pickle.dump(data, open(self.dump_file, "wb"))

    def _load_dump(self):
        if self.dump_file.exists():
            return pickle.load(open(self.dump_file, "rb"))

    def search_customers(self):
        found_customers = dict()
        notfound_customers = dict()

        if self.dump_file.exists():
            print("loading from pickle, please delete to loop through db again")
            data = self._load_dump()
            return data

        for forest in self.forests.values():
            last_customer_related = None
            for owner in forest.owners:
                _customer = CustomerService.has_owner(owner)

                if _customer:
                    self.keep_customers(_customer, forest, found_customers)
                    last_customer_related = _customer
                else:
                    _keep_data = dict(owner=owner, related=last_customer_related)
                    self.keep_customers(_keep_data, forest, notfound_customers)

        print(len(found_customers), len(notfound_customers))

        data = dict(
            found_customers=found_customers, notfound_customers=notfound_customers
        )

        self._create_dump(data)

        return data

    def keep_customers(self, _customer, forest, customers):
        if forest.internal_id not in customers:
            customers[forest.internal_id] = []
        customers[forest.internal_id].append(_customer)

    def link_forest_customer(self):
        data = self._load_dump()
        self.insert_found_customers(data["found_customers"])
        self.insert_notfound_customers(data["notfound_customers"])

    def insert_found_customers(self, data: dict):
        # simply create connection between customer and forest
        for forest_id in data.keys():
            customers = [customer for customer in data.get(forest_id)]
            for customer in customers:
                customer_id = (
                    customer.pk
                    if customer.internal_id is None or len(customer.internal_id) == 0
                    else customer.internal_id
                )

                print(f"Linking forest {forest_id} with customer {customer_id}")
                ForestService.create_forest_customer_relation(
                    forest_id, customer.pk, forest_internal=True
                )

    def insert_notfound_customers(self, data: dict):
        # mark forest attributes["related_owners_count"]
        # with human name: create new customer, link with new customer
        for forest_id in data.keys():
            items = [item for item in data.get(forest_id)]
            # item
            # dict(owner=, related=)
            for item in items:
                owner = item.get("owner")
                related = item.get("related")
                related_count = parse_name_extra(owner.name_kanji.last_name)
                if related_count is not None and related_count > 0:
                    ForestService.mark_related_count(
                        forest_id, related_count, forest_internal=True
                    )
                else:
                    contact = CustomerService.get_basic_contact(related.pk)
                    customer = CustomerSchema(
                        id=uuid4().hex,
                        name_kanji=owner.name_kanji,
                        name_kana=owner.name_kana,
                        address=owner.address,
                        banking=Banking.parse_obj(related.banking),
                    )
                    CustomerService.create_customer(customer, link_contact=contact)
