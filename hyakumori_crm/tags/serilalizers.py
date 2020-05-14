from rest_framework import serializers

from hyakumori_crm.tags.models import TagSetting


class TagSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagSetting
        fields = ["id", "created_at", "updated_at", "attributes", "name", "code"]
