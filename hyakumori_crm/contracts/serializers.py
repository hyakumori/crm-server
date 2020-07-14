from rest_framework import serializers

from .models import ContractType


class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = [
            "id",
            "created_at",
            "updated_at",
            "attributes",
            "name",
            "code",
            "description",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "attributes",
            "code",
            "description",
        ]

    def create(self, validated_data):
        c = ContractType(
            **validated_data,
            code=validated_data["name"],
            attributes={"assignable": True}
        )
        c.save()
        return c
