"""
メニュー
管理	登録	設定
森林	協議	アカウント
顧客	顧客	ユーザー
協議	郵送

検索条件
基本情報	契約情報	    森林情報
土地管理ID	契約タイプ	    面積
地籍	    契約開始	    樹幹長
顧客名	    契約終了	    収量比数
顧客住所	FSC認証可否	    林相名
契約形態	作業契約開始	形状比
ステータス	作業契約終了	立木本数

アクション
一括編集
契約ステータス
契約開始/終了月
施業中/完了
"""

from model_utils import Choices
from django.db import models


class CustomerRegisterStatuses(models.TextChoices):
    REGISTERED = 'registered', '登録済'
    UNREGISTERED = 'unregistered', '未登録'


class ContractStatuses(models.TextChoices):
    NEGOTIATING = 'negotiating', '交渉中'
    UNDER_CONCLUSION = 'under_conclusion', '締結中'
    NOT_SIGNED = 'not_signed', '未締結'
