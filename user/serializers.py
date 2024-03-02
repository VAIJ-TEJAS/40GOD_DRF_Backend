from rest_framework import serializers
from .models import User, AddressBook


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True, "required": True}}


class AddressBookSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = AddressBook
        fields = "__all__"