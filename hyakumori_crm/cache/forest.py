import logging
from typing import List

from django.db.models import Prefetch
from django.db.models.expressions import RawSQL

from hyakumori_crm.crm.common.utils import get_customer_name
from hyakumori_crm.crm.models import ForestCustomer, Forest
import time

logger = logging.Logger(__name__)


def refresh_customer_forest_cache(forest_ids: List[str]):
    forest_filters = dict()
    now = time.time()

    forest_filters["id__in"] = forest_ids

    forests = Forest.objects.filter(**forest_filters).prefetch_related(
        Prefetch(
            "forestcustomer_set",
            queryset=ForestCustomer.objects.order_by(
                RawSQL("attributes->'default'", params=[]).desc(nulls_last=True),
                "created_at",
            ),
        ),
        "forestcustomer_set__customer",
        "forestcustomer_set__customer__customercontact_set",
        "forestcustomer_set__customer__customercontact_set__contact",
    )
    for f in forests:
        try:
            # WARNING: postgres jsonb saved not in order
            customer_list = {
                str(fc.customer_id): dict(
                    default=fc.attributes.get("default", False),
                    contact_id=str(fc.customer.self_contact.id),
                    name_kanji=fc.customer.self_contact.name_kanji,
                    name_kana=fc.customer.self_contact.name_kana,
                )
                for fc in f.forestcustomer_set.all()
            }
            repr_name_kanji = ",".join(
                get_customer_name(item.get("name_kanji"))
                for item in customer_list.values()
            )
            repr_name_kana = ",".join(
                get_customer_name(item.get("name_kana"))
                for item in customer_list.values()
            )
            f.attributes["customer_cache"] = dict(
                list=customer_list,
                repr_name_kanji=repr_name_kanji,
                repr_name_kana=repr_name_kana,
            )
            f.save(update_fields=["attributes", "updated_at"])
        except Exception as e:
            logger.warning(
                f"could not saving latest user self contact info in forest: {f.pk}",
                exc_info=e,
            )

    logger.debug(f"Cache reloading has been finished, time cost: {time.time() - now}s")
