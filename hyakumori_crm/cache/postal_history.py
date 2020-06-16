import logging

from django.db.models import Value, F
from django.db.models.functions import Concat
from django.db.models.signals import post_save
from django.dispatch import receiver

from hyakumori_crm.crm.common.utils import get_customer_name
from hyakumori_crm.crm.models import PostalHistory, Customer, Forest
from hyakumori_crm.users.models import User

logger = logging.Logger(__name__)


def refresh_user_participants_cache(postalhistory: PostalHistory, save=False):
    try:
        postalhistory.attributes["user_cache"] = dict(
            count=postalhistory.postalhistoryuser_set.count(),
            list=list(
                postalhistory.postalhistoryuser_set.all()
                .annotate(
                    full_name=Concat("user__last_name", Value(" "), "user__first_name")
                )
                .values("user_id", "full_name")
            ),
        )
        postalhistory.attributes["user_cache"]["repr"] = (
            ",".join(
                list(
                    map(
                        lambda c: c["full_name"],
                        postalhistory.attributes["user_cache"]["list"],
                    )
                )
            )
            or None
        )
        if save:
            postalhistory.save()
    except:
        logging.warning(
            f"could not refresh user cache for postalhistory: {postalhistory.pk}"
        )
    finally:
        return postalhistory


def refresh_forest_cache(postalhistory: PostalHistory, save=False):
    try:
        postalhistory.attributes["forest_cache"] = dict(
            count=postalhistory.postalhistoryforest_set.count(),
            list=list(
                postalhistory.postalhistoryforest_set.all().values(
                    "forest__internal_id"
                )
            ),
        )
        postalhistory.attributes["forest_cache"]["repr"] = (
            ",".join(
                list(
                    map(
                        lambda c: c["forest__internal_id"],
                        postalhistory.attributes["forest_cache"]["list"],
                    )
                )
            )
            or None
        )
        if save:
            postalhistory.save()
    except:
        logging.warning(
            f"could not refresh user cache for postalhistory: {postalhistory.pk}"
        )
    finally:
        return postalhistory


def refresh_customers_cache(postalhistory: PostalHistory, save=False):
    try:
        postalhistory.attributes["customer_cache"] = dict(
            count=postalhistory.postalhistorycustomer_set.count(),
            list=list(
                postalhistory.postalhistorycustomer_set.all()
                .annotate(
                    customer__name_kanji=F(
                        "postalhistorycustomercontact__customercontact__contact__name_kanji"
                    ),
                    customer__name_kana=F(
                        "postalhistorycustomercontact__customercontact__contact__name_kana"
                    ),
                )
                .values("customer__id", "customer__name_kanji", "customer__name_kana")
            ),
        )
        customer_repr = []
        for c in postalhistory.attributes["customer_cache"]["list"]:
            kanji_name = c["customer__name_kanji"]
            customer_name = get_customer_name(kanji_name)
            customer_repr.append(customer_name)

        postalhistory.attributes["customer_cache"]["repr"] = (
            ",".join(customer_repr) or None
        )
        if save:
            postalhistory.save()
    except:
        logging.warning(
            f"could not refresh user cache for postalhistory: {postalhistory.pk}"
        )
    finally:
        return postalhistory


def refresh_single_postalhistory_cache(postalhistory: PostalHistory):
    refresh_customers_cache(postalhistory, save=False)
    refresh_user_participants_cache(postalhistory, save=False)
    refresh_forest_cache(postalhistory, save=False)
    postalhistory.save(update_fields=["attributes", "updated_at"])
    return postalhistory


@receiver(post_save, sender=Customer)
def update_customer_cache(sender, instance, created, **kwargs):
    if not created:
        try:
            for postalhistorycustomer in instance.postalhistorycustomer_set.iterator():
                refresh_customers_cache(postalhistorycustomer.postalhistory, save=True)
        except:
            logger.warning(
                f"could not refresh customer cache for postalhistory, customer: {instance.pk}"
            )


@receiver(post_save, sender=User)
def update_user_cache(sender, instance, created, **kwargs):
    if not created:
        try:
            for postalhistoryuser in instance.postalhistoryuser_set.iterator():
                refresh_user_participants_cache(
                    postalhistoryuser.postalhistory, save=True
                )
        except:
            logger.warning(
                f"could not refresh user cache for postalhistory, user: {instance.pk}"
            )


@receiver(post_save, sender=Forest)
def update_forest_cache(sender, instance, created, **kwargs):
    if not created:
        try:
            for postalhistoryforest in instance.postalhistoryforest_set.iterator():
                refresh_forest_cache(postalhistoryforest.postalhistory, save=True)
        except:
            logger.warning(
                f"could not refresh forest cache for postalhistory, forest: {instance.pk}"
            )
