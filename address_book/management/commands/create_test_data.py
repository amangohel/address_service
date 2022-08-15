from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
from rest_framework.authtoken.models import Token

from address_book.models import AddressBook


class Command(BaseCommand):
    help = "Generate a test user as well as a token for that user"

    def add_arguments(self, parser):
        parser.add_argument("count", nargs="+", type=int)

    def handle(self, *args, **options):
        User.objects.all().delete()
        AddressBook.objects.all().delete()

        fake = Faker()
        count = options["count"][0]

        # Create a user
        user = User.objects.create_user(
            username=fake.name(), email=fake.email(), password="password"
        )

        # generate a token for the user
        token = Token.objects.create(user=user)
        if count:
            for _ in range(0, count):
                AddressBook.objects.create(
                    user=user,
                    country=fake.country(),
                    address_line_one=fake.address(),
                    city=fake.city(),
                    zip_code=fake.postcode(),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {count} addresses for user {user} with email {user.email} and token {token.key}"
            )
        )
