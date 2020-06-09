import logging

from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models.signals import post_save
from django.dispatch import receiver

from hyakumori_crm.crm.common.utils import get_customer_name
from hyakumori_crm.crm.models import Archive, Customer, Forest
from hyakumori_crm.users.models import User

logger = logging.Logger(__name__)


def refresh_user_participants_cache(archive: Archive, save=False):
    try:
        archive.attributes["user_cache"] = dict(
            count=archive.archiveuser_set.count(),
            list=list(
                archive.archiveuser_set.all()
                .annotate(
                    full_name=Concat("user__last_name", Value(" "), "user__first_name")
                )
                .values("user_id", "full_name")
            ),
        )
        archive.attributes["user_cache"]["repr"] = ",".join(
            list(
                map(lambda c: c["full_name"], archive.attributes["user_cache"]["list"])
            )
        )
        if save:
            archive.save()
    except:
        logging.warning(f"could not refresh user cache for archive: {archive.pk}")
    finally:
        return archive


def refresh_forest_cache(archive: Archive, save=False):
    try:
        archive.attributes["forest_cache"] = dict(
            count=archive.archiveforest_set.count(),
            list=list(archive.archiveforest_set.all().values("forest__internal_id")),
        )
        archive.attributes["forest_cache"]["repr"] = ",".join(
            list(
                map(
                    lambda c: c["forest__internal_id"],
                    archive.attributes["forest_cache"]["list"],
                )
            )
        )
        if save:
            archive.save()
    except:
        logging.warning(f"could not refresh user cache for archive: {archive.pk}")
    finally:
        return archive


def refresh_customers_cache(archive: Archive, save=False):
    try:
        archive.attributes["customer_cache"] = dict(
            count=archive.archivecustomer_set.count(),
            list=list(
                archive.archivecustomer_set.all().values(
                    "customer__id", "customer__name_kanji", "customer__name_kana"
                )
            ),
        )
        customer_repr = []
        for c in archive.attributes["customer_cache"]["list"]:
            kanji_name = c["customer__name_kanji"]
            customer_name = get_customer_name(kanji_name)
            customer_repr.append(customer_name)

        archive.attributes["customer_cache"]["repr"] = ",".join(customer_repr)
        if save:
            archive.save()
    except:
        logging.warning(f"could not refresh user cache for archive: {archive.pk}")
    finally:
        return archive


def refresh_single_archive_cache(archive: Archive):
    refresh_customers_cache(archive, save=False)
    refresh_user_participants_cache(archive, save=False)
    refresh_forest_cache(archive, save=False)
    archive.save(update_fields=["attributes", "updated_at"])
    return archive


@receiver(post_save, sender=Customer)
def update_customer_cache(sender, instance, created, **kwargs):
    if not created:
        try:
            for archivecustomer in instance.archivecustomer_set.iterator():
                refresh_customers_cache(archivecustomer.archive, save=True)
        except:
            logger.warning(
                f"could not refresh customer cache for archive, customer: {instance.pk}"
            )


@receiver(post_save, sender=User)
def update_user_cache(sender, instance, created, **kwargs):
    if not created:
        try:
            for archiveuser in instance.archiveuser_set.iterator():
                refresh_user_participants_cache(archiveuser.archive, save=True)
        except:
            logger.warning(
                f"could not refresh user cache for archive, user: {instance.pk}"
            )


@receiver(post_save, sender=Forest)
def update_forest_cache(sender, instance, created, **kwargs):
    if not created:
        try:
            for archiveforest in instance.archiveforest_set.iterator():
                refresh_forest_cache(archiveforest.archive, save=True)
        except:
            logger.warning(
                f"could not refresh forest cache for archive, forest: {instance.pk}"
            )
