class ForestActions:
    created = ("forest.created", "森林情報が作成されました。", "mdi-image-filter-hdr")
    basic_info_updated = ("forest.basic_info_updated", "基本情報が更新されました。", "mdi-launch")
    customers_updated = ("forest.customers_updated", "所有者情報が更新されました。", "mdi-face")
    postal_info_updated = (
        "forest.postal_info_updated",
        "書類郵送記録が更新されました。",
        "mdi-email-multiple-outline",
    )
    memo_info_updated = (
        "forest.memo_info_updated",
        "備考記録が更新されました。",
        "mdi-clipboard-list-outline",
    )


class CustomerActions:
    created = ("customer.created", "顧客データが作成されました。", "mdi-face")
    basic_info_updated = ("customer.basic_info_updated", "顧客情報が更新されました。", "mdi-launch")
    banking_info_updated = ("customer.banking_info_updated", "顧客口座情報が更新されました。", "mdi-bank")
    customers_updated = (
        "customer.customers_updated",
        "所有林情報が更新されました。",
        "mdi-account-group",
    )
    forests_updated = (
        "customer.forests_updated",
        "森林情報が更新されました。",
        "mdi-account-group",
    )
    direct_contacts_updated = (
        "customer.direct_contacts_updated",
        "連絡者情報が更新されました。",
        "mdi-contacts-outline",
    )
    family_contacts_updated = (
        "customer.family_contacts_updated",
        "家族情報が更新されました。",
        "mdi-contacts-outline",
    )
    other_contacts_updated = (
        "customer.other_contacts_updated",
        "その他関係者情報が更新されました。",
        "mdi-contacts-outline",
    )
    memo_info_updated = (
        "customer.memo_info_updated",
        "備考記録が更新されました。",
        "mdi-clipboard-list-outline",
    )


class ArchiveActions:
    created = ("archive.created", "協議データが作成されました。", "mdi-calendar-text")
    basic_info_updated = ("archive.basic_info_updated", "協議情報が更新されました。", "mdi-launch")
    materials_updated = (
        "archive.materials_updated",
        "配布資料が更新されました。",
        "mdi-clipboard-multiple-outline",
    )
    customer_participants_updated = (
        "archive.customer_participants_updated",
        "先方参加者が更新されました。",
        "mdi-face",
    )
    staff_participants_updated = (
        "archive.staff_participants_updated",
        "当方参加者が更新されました。",
        "mdi-account-check-outline",
    )
    forest_list_updated = (
        "archive.forest_list_updated",
        "関連する森林が更新されました。",
        "mdi-image-filter-hdr",
    )


class UserActions:
    created = ("user.created", "ユーザデータが作成されました。", "mdi-account-edit-outline")
    basic_info_updated = ("user.basic_info_updated", "基本情報が更新されました。", "mdi-launch")
    email_invitation_sent = (
        "user.email_invitation_sent",
        "招待メールが送信されました。",
        "mdi-email-check-outline",
    )
    account_activated = (
        "user.account_activated",
        "アカウントが有効化されました。",
        "mdi-account-check-outline",
    )
    status_updated = (
        "user.status_updated",
        "ステータスが更新されました。",
        "mdi-account-cog-outline",
    )
    group_updated = ("user.group_updated", "グループ情報が更新されました。", "mdi-account-group")
