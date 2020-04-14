from rest_framework.serializers import ModelSerializer

from ..models import Customer, Contact, Forest


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "internal_id", "name_kanji", "name_kana", "address", "banking", "tags"]


class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        exclude = ['contact_info', 'deleted', 'author', 'editor']


class ForestSerializer(ModelSerializer):
    class Meta:
        model = Forest
        exclude = ['deleted', 'author', 'editor']
