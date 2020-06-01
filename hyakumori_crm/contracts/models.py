from django.db import models
from django.utils.translation import ugettext_lazy as _

from hyakumori_crm.core.models import UUIDPrimary, TimestampMixin, AttributesMixin


class ContractType(UUIDPrimary, TimestampMixin, AttributesMixin):
    name = models.CharField(unique=True, max_length=255, blank=False, null=False, verbose_name=_("contract type name"))
    code = models.CharField(unique=True, max_length=255, blank=False, null=False,
                            verbose_name=_("contract code name, reversed enum value"))
    description = models.TextField(blank=True, null=True, verbose_name=_("contract type description"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("contract type")
        verbose_name_plural = _("contract type")

    def __str__(self):
        return _("ContractType, id: {id}").format(id=self.id)
