from .enums import SystemGroups


def can_view_forests(request, user):
    return (
        user.member_of(SystemGroups.GROUP_LIMITED_USER)
        or user.member_of(SystemGroups.GROUP_ADMIN)
        or user.member_of(SystemGroups.GROUP_NORMAL_USER)
    )


def can_view_customers(request, user):
    return user.member_of(SystemGroups.GROUP_ADMIN) or user.member_of(
        SystemGroups.GROUP_NORMAL_USER
    )


def can_view_archives(request, user):
    return (
        user.member_of(SystemGroups.GROUP_ADMIN)
        or user.member_of(SystemGroups.GROUP_NORMAL_USER)
        or user.member_of(SystemGroups.GROUP_LIMITED_USER)
    )
