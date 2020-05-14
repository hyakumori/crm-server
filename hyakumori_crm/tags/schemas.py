from typing import List

from hyakumori_crm.core.models import HyakumoriDanticModel
from pydantic.color import Color


class ColorMapInput(HyakumoriDanticModel):
    value: str
    color: Color


class TagSettingInput(HyakumoriDanticModel):
    id: str = None
    name: str
    code: str
    color_maps: List[ColorMapInput]


class AssignTagItem(HyakumoriDanticModel):
    tag_name: str
    value: str


class TagDeleteInput(HyakumoriDanticModel):
    id: str


class AssignTagInput(HyakumoriDanticModel):
    object_id: str
    tags: List[AssignTagItem] = []


class TagKeyMigrateInput(HyakumoriDanticModel):
    object_ids: List[str]
    from_key: str
    to_key: str
    do_update: bool = False


class TagKeyMigrateAllInput(HyakumoriDanticModel):
    from_key: str
    to_key: str
    do_update: bool = False
