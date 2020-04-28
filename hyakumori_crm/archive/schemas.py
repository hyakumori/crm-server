from datetime import datetime
from typing import Optional

from ..core.models import HyakumoriDanticModel


class ArchiveInput(HyakumoriDanticModel):
    title: str
    content: Optional[str]
    location: Optional[str]
    future_action: Optional[str]
    archive_date: Optional[datetime]

