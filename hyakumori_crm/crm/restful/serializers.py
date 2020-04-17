from rest_framework.serializers import ModelSerializer, UUIDField

from ..models import Customer, Contact, Forest


class ContactSerializer(ModelSerializer):
    forest_id = UUIDField(read_only=True)

    class Meta:
        model = Contact
        exclude = ["contact_info", "deleted"]


class CustomerSerializer(ModelSerializer):
    self_contact = ContactSerializer()

    class Meta:
        model = Customer
        fields = ["id", "internal_id", "attributes", "tags", "banking", "self_contact"]


class ForestSerializer(ModelSerializer):
    class Meta:
        model = Forest
        exclude = ["deleted"]
