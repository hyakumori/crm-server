import logging
from typing import List

from hyakumori_crm.crm.common.utils import get_customer_name
from hyakumori_crm.crm.models import ForestCustomer, Forest
import time

logger = logging.Logger(__name__)


def refresh_customer_forest_cache(forest_ids: List[str]):
    filters = dict()
    forest_filters = dict()
    now = time.time()

    if len(forest_ids) > 0:
        filters["forest_id__in"] = forest_ids
        forest_filters["id__in"] = forest_ids

    forests = Forest.objects.filter(**forest_filters)
    for forest in forests.iterator():
        forest.attributes["customer_cache"] = dict(list=dict(), repr_name_kanji="", repr_name_kana="")
        forest.save()

    forestcustomers = ForestCustomer.objects \
        .filter(**filters) \
        .select_related("customer", "forest")

    for fc in forestcustomers.iterator():
        try:
            forest = fc.forest
            customer = fc.customer
            self_contact_qs = fc.customer.customercontact_set.filter(is_basic=True).first()
            if not self_contact_qs:
                raise Exception(f"self contact not existed for customer: {customer.id}")

            self_contact = self_contact_qs.contact
            forest.refresh_from_db()

            _repr_name_kanji = []
            _repr_name_kana = []

            customer_id = str(customer.id)
            if customer_id in forest.attributes["customer_cache"]["list"]:
                del forest.attributes["customer_cache"]["list"][customer_id]

            forest.attributes["customer_cache"]["list"][customer_id] = dict(
                contact_id=str(self_contact.id),
                name_kanji=self_contact.name_kanji,
                name_kana=self_contact.name_kana)

            for _, item in forest.attributes["customer_cache"]["list"].items():
                _repr_name_kanji.append(get_customer_name(item.get("name_kanji")))
                _repr_name_kana.append(get_customer_name(item.get("name_kana")))

            forest.attributes["customer_cache"]["repr_name_kanji"] = ",".join(_repr_name_kanji)
            forest.attributes["customer_cache"]["repr_name_kana"] = ",".join(_repr_name_kana)
            forest.save(update_fields=["attributes", "updated_at"])
        except Exception as e:
            logger.warning(
                f"could not saving latest user self contact info in forest: {fc.forest.pk}", exc_info=e
            )

    logger.debug(f"Cache reloading has been finished, time cost: {time.time() - now}s")
