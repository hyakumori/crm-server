UNKNOWN = "Unknown"
EMPTY = ""
DEFAULT_EMAIL = "name@example.com"
FOREST_ATTRIBUTES = [
    "地番面積_ha",
    "面積_ha",
    "面積_m2",
    "平均傾斜度",
    "第1林相ID",
    "第1林相名",
    "第1Area",
    "第1面積_ha",
    "第1立木本",
    "第1立木密",
    "第1平均樹",
    "第1樹冠長",
    "第1平均DBH",
    "第1合計材",
    "第1ha材積",
    "第1収量比",
    "第1相対幹",
    "第1形状比",
    "第2林相ID",
    "第2林相名",
    "第2Area",
    "第2面積_ha",
    "第2立木本",
    "第2立木密",
    "第2平均樹",
    "第2樹冠長",
    "第2平均DBH",
    "第2合計材",
    "第2ha材積",
    "第2収量比",
    "第2相対幹",
    "第2形状比",
    "第3林相ID",
    "第3林相名",
    "第3Area",
    "第3面積_ha",
    "第3立木本",
    "第3立木密",
    "第3平均樹",
    "第3樹冠長",
    "第3平均DBH",
    "第3合計材",
    "第3ha材積",
    "第3収量比",
    "第3相対幹",
    "第3形状比",
]
FOREST_LAND_ATTRIBUTES = ["地番本番", "地番支番", "地目", "林班", "小班", "区画"]

# Predefined key mapping for customer tags
# If this growing, consider a mapping table in DB
CUSTOMER_TAG_KEYS = dict(status="未登録/登録", ranking="所有者順位", same_name="同姓同名",)

FOREST_TAG_KEYS = dict(danchi="団地", manage_type="管理形態")

FOREST_CADASTRAL = ["地籍_都道府県", "地籍_市町村", "地籍_大字", "地籍_字"]

FOREST_OWNER_NAME = ["土地所有者名_漢字", "土地所有者名_カナ"]

FOREST_OWNER_ADDRESS = ["土地所有者住所_都道府県", "土地所有者住所_市町村", "土地所有者住所_大字"]

FOREST_CONTRACT = ["長期契約", "開始日", "終了日", "作業道契約", "開始日", "終了日", "FSC認証加入", "開始日", "終了日"]

CUSTOMER_ID_PREFIX = "DFFC"
CUSTOMER_ID_SEQUENCE = "customer_ids"
