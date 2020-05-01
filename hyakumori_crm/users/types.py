from pydantic import EmailStr, Field

from hyakumori_crm.core.models import HyakumoriDanticModel


class UserUpdateInput(HyakumoriDanticModel):
    email: EmailStr
    username: str = Field(..., min_length=3)
