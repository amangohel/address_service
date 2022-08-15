import factory
from django.contrib.auth.models import User

from address_book.models import AddressBook


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("name")
    email = factory.Faker("email")
    password = factory.Faker("password")


class AddressBookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AddressBook

    user = factory.SubFactory(UserFactory)
    country = factory.Faker("country")
    address_line_one = factory.Faker("address")
    city = factory.Faker("city")
    zip_code = factory.Faker("postcode")
