from rest_framework import serializers

from .models import ContractType


class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = ["id", "created_at", "updated_at", "attributes", "name", "code", "description"]
