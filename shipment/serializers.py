from rest_framework import serializers
from user.models import AddressBook
from .models import Shipment


class ShipmentAddressBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressBook
        fields = "__all__"


class ShipmentSerializer(serializers.ModelSerializer):
    address_details = ShipmentAddressBookSerializer(source="address", read_only=True)

    class Meta:
        model = Shipment
        fields = ["id", "user", "date", "address", "address_details"]
        extra_kwargs = {"user": {"read_only": True}, "address": {"write_only": True}}
