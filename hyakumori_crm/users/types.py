from uuid import UUID
from typing import List

from pydantic import EmailStr, Field

from hyakumori_crm.core.models import HyakumoriDanticModel


class UserUpdateInput(HyakumoriDanticModel):
    email: EmailStr
    username: str = Field(..., min_length=3)


class GroupAssginmentInput(HyakumoriDanticModel):
    user_id: UUID
    group_ids: List[int]


class PermissionAssignmentInput(HyakumoriDanticModel):
    user_id: UUID
    object_id: UUID
    object_type_id: int
    permission_ids: List[int]
