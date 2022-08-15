import json
import uuid

from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from address_book.models import AddressBook
from tests.factories import AddressBookFactory, UserFactory


class TestDeleteAddress(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.login(username=cls.user.username, password="password")
        cls.token = Token.objects.create(user=cls.user)
        cls.api_client.credentials(HTTP_AUTHORIZATION="Token " + cls.token.key)

    def setUp(self):
        for i in range(3):
            AddressBookFactory(
                id=uuid.UUID(int=i),
                user=self.user,
                country=self.fake.country(),
                address_line_one=self.fake.address(),
                city=self.fake.city(),
                zip_code=self.fake.postcode(),
            )

    def test_delete_single_address(self):
        response = self.api_client.delete(
            reverse("addresses"),
            data=json.dumps(
                {
                    "address_ids": [
                        "00000000-0000-0000-0000-000000000001",
                    ]
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 204

    def test_delete_multiple_addresses(self):
        response = self.api_client.delete(
            reverse("addresses"),
            data=json.dumps(
                {
                    "address_ids": [
                        "00000000-0000-0000-0000-000000000001",
                        "00000000-0000-0000-0000-000000000002",
                    ]
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 204
        assert AddressBook.objects.count() == 1
