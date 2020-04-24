from django.contrib.auth.models import Permission, Group
from rest_framework import serializers

from hyakumori_crm.permissions.enums import SystemGroups


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        exclude = ("content_type",)


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(read_only=True, many=True)
    codename = serializers.SerializerMethodField('get_group_codename')

    def get_group_codename(self, obj):
        try:
            return SystemGroups(obj.name).name.lower()
        except ValueError:
            return obj.name

    class Meta:
        model = Group
        fields = "__all__"
