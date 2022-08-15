import pycountry
from django.contrib.auth.models import User
from rest_framework import serializers

from address_book.models import AddressBook


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username"]


class AddressBookSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    country = serializers.CharField(max_length=2, min_length=2)
    address_line_one = serializers.CharField(max_length=50)
    address_line_two = serializers.CharField(allow_blank=True, max_length=50, allow_null=True)
    city = serializers.CharField(max_length=50)
    zip_code = serializers.CharField(max_length=10)

    def create(self, validated_data):
        return AddressBook.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.country = validated_data.get("country", instance.country)
        instance.address_line_one = validated_data.get(
            "address_line_one", instance.address_line_one
        )
        instance.address_line_two = validated_data.get(
            "address_line_two", instance.address_line_two
        )
        instance.city = validated_data.get("city", instance.city)
        instance.zip_code = validated_data.get("zip_code", instance.zip_code)
        instance.save()
        return instance

    @classmethod
    def address_exists_for_user(cls, user, address_line_one, zip_code) -> bool:
        """
        Check if an address already exists in the address book
        """
        return (
            AddressBook.objects.filter(
                user=user, address_line_one=address_line_one, zip_code=zip_code
            ).count()
            > 0
        )

    def validate(self, data):
        if not pycountry.countries.get(alpha_2=data["country"]):
            raise serializers.ValidationError("Country is not valid")
        if len(data["zip_code"]) > 10:
            raise serializers.ValidationError("Zip code can be up to 10 characters long")
        if len(data["address_line_one"]) > 50:
            raise serializers.ValidationError("Address line one is too long")
        if data["address_line_two"]:
            if len(data["address_line_two"]) > 50:
                raise serializers.ValidationError("Address line two is too long")
        if len(data["city"]) > 50:
            raise serializers.ValidationError("City is too long")

        return data
