from enum import Enum


class SystemGroups(str, Enum):
    GROUP_ADMIN = "管理者"
    GROUP_NORMAL_USER = "一般ユーザ"
    GROUP_LIMITED_USER = "限定ユーザ"
