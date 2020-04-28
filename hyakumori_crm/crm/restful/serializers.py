from rest_framework.serializers import (
    ModelSerializer,
    UUIDField,
    IntegerField,
    JSONField,
    SerializerMethodField
)

from ..models import Customer, Contact, Forest, Attachment, Archive
from ...users.serializers import UserSerializer


class ContactSerializer(ModelSerializer):
    forest_id = UUIDField(read_only=True)
    cc_attrs = JSONField(read_only=True)

    class Meta:
        model = Contact
        exclude = ["contact_info", "deleted"]


class CustomerSerializer(ModelSerializer):
    self_contact = ContactSerializer()
    forests_count = IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "internal_id",
            "attributes",
            "tags",
            "banking",
            "self_contact",
            "forests_count",
        ]


class ForestSerializer(ModelSerializer):
    class Meta:
        model = Forest
        exclude = ["deleted"]


class AttachmentSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            "id",
            "object_id",
            "content_type",
            "creator",
            "filename",
        ]


class ArchiveSerializer(ModelSerializer):
    attachments = SerializerMethodField()
    author = UserSerializer()

    class Meta:
        model = Archive
        fields = [
            "id",
            "title",
            "content",
            "location",
            "future_action",
            "archive_date",
            "author",
            "attachments"
        ]

    def get_attachments(self, obj: Archive):
        try:
            return AttachmentSerializer(Attachment.objects.filter(object_id=obj.id), many=True).data
        except Attachment.DoesNotExist:
            return []
