from rest_framework import serializers

from hyakumori_crm.activity.models import ActionLog


class ActionLogSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField("get_user_fullname")
    message = serializers.CharField(read_only=True, allow_blank=True)

    def get_user_fullname(self, obj):
        return obj.user.full_name

    class Meta:
        model = ActionLog
        fields = ("id", "template_data", "created_at", "author", "message")
