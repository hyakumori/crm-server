from rest_framework.serializers import (
    ModelSerializer,
    UUIDField,
    IntegerField,
    JSONField,
    BooleanField,
    SerializerMethodField,
    CharField,
)
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Customer, Contact, Forest, Attachment, Archive
from ...contracts.models import ContractType
from ...forest.service import map_forests_contracts
from ...users.serializers import UserSerializer


class ContactSerializer(ModelSerializer):
    forest_internal_id = CharField(read_only=True)
    forest_id = UUIDField(read_only=True)
    forestcustomer_id = UUIDField(read_only=True)
    customer_id = UUIDField(read_only=True)
    owner_customer_id = UUIDField(read_only=True)
    cc_attrs = JSONField(read_only=True)
    # forest customer contact default
    default = BooleanField(read_only=True)
    is_basic = BooleanField(read_only=True)
    forests_count = IntegerField(read_only=True)
    business_id = CharField(read_only=True)

    class Meta:
        model = Contact
        exclude = ["contact_info", "deleted"]


class CustomerContactSerializer(ModelSerializer):
    customer_id = UUIDField(read_only=True)
    customer_name_kanji = JSONField(read_only=True)
    cc_attrs = JSONField(read_only=True)
    is_basic = BooleanField(read_only=True)
    forests_count = IntegerField(read_only=True)
    business_id = CharField(read_only=True)

    class Meta:
        model = Contact
        exclude = ["contact_info", "deleted"]


class CustomerSerializer(ModelSerializer):
    self_contact = ContactSerializer()
    forests_count = IntegerField(read_only=True)
    # forest default owner
    default = BooleanField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "business_id",
            "internal_id",
            "attributes",
            "tags",
            "banking",
            "self_contact",
            "forests_count",
            "default",
        ]


class LimittedCustomerSerializer(CustomerSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "business_id",
            "internal_id",
            "attributes",
            "self_contact",
            "forests_count",
            "default",
            "tags",
        ]


class ForestSerializer(GeoFeatureModelSerializer):
    contracts = SerializerMethodField()

    class Meta:
        model = Forest
        geo_field = "geom"
        exclude = ["deleted"]

    def get_contracts(self, forest):
        contract_types = dict(ContractType.objects.values_list("code", "name"))
        return map_forests_contracts(forest, contract_types).contracts


class ForestListingSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Forest
        geo_field = "geom"
        fields = [
            "id",
            "internal_id",
            "cadastral",
            "customers_count",
            "tags",
            "land_attributes",
        ]


class AttachmentSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            "id",
            "object_id",
            "content_type",
            "creator",
            "filename",
            "attributes",
            "size",
            "download_url",
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
            "attachments",
            "attributes",
            "tags",
        ]

    def get_attachments(self, obj: Archive):
        try:
            return AttachmentSerializer(
                Attachment.objects.filter(object_id=obj.id), many=True
            ).data
        except Attachment.DoesNotExist:
            return []


class ArchiveListingSerializer(ModelSerializer):
    author_name = SerializerMethodField(method_name="get_author_name")

    def get_author_name(self, obj: Archive):
        return obj.author.full_name

    class Meta:
        model = Archive
        fields = [
            "id",
            "title",
            "content",
            "author_name",
            "location",
            "future_action",
            "archive_date",
            "attributes",
            "tags",
        ]
