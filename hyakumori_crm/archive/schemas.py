from datetime import datetime
from typing import Optional

from ..core.models import HyakumoriDanticModel


class ArchiveInput(HyakumoriDanticModel):
    title: str
    content: Optional[str]
    location: Optional[str]
    future_action: Optional[str]
    archive_date: Optional[datetime]


class ArchiveFilter(HyakumoriDanticModel):
    id: str = None
    sys_id: str = None
    archive_date: str = None
    title: str = None
    content: str = None
    author: str = None
    location: str = None
    their_participants: str = None
    our_participants: str = None
    associated_forest: str = None

    class Config:
        arbitrary_types_allowed = True
        min_anystr_length = 0
