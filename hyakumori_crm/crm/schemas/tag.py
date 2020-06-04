from typing import List
from uuid import UUID

from hyakumori_crm.core.models import HyakumoriDanticModel


class TagBulkUpdate(HyakumoriDanticModel):
    ids: List[UUID]
    key: str
    value: str
