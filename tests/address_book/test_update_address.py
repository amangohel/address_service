import json
import uuid

from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tests.factories import AddressBookFactory, UserFactory


class TestUpdateAddress(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.login(username=cls.user.username, password="password")
        cls.token = Token.objects.create(user=cls.user)
        cls.api_client.credentials(HTTP_AUTHORIZATION="Token " + cls.token.key)

    def test_update_address(self):
        address = AddressBookFactory(
            user=self.user,
            country=self.fake.country(),
            address_line_one=self.fake.address(),
            city=self.fake.city(),
            zip_code=self.fake.postcode(),
        )

        response = self.api_client.put(
            reverse("get_and_update_address", kwargs={"address_id": address.id}),
            data=json.dumps(
                {
                    "country": "US",
                    "address_line_one": "1 Testerson Street",
                    "address_line_two": "Test Town",
                    "city": "Bean City",
                    "zip_code": "TE1 1ST",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json() == {
            "country": "US",
            "address_line_one": "1 Testerson Street",
            "address_line_two": "Test Town",
            "city": "Bean City",
            "zip_code": "TE1 1ST",
        }

    def test_update_fails_if_existing_address(self):
        # Address line one and zip code are composed together
        # to uniquely identify an address
        address_line_one = "1 Test Street"
        zip_code = "TE1 1ST"

        address = AddressBookFactory(
            user=self.user,
            country="GB",
            address_line_one=address_line_one,
            address_line_two="address_line_two",
            city="city",
            zip_code=zip_code,
        )

        response = self.api_client.put(
            reverse("get_and_update_address", kwargs={"address_id": address.id}),
            data=json.dumps(
                {
                    "country": "GB",
                    "address_line_one": address_line_one,
                    "address_line_two": "some random value",
                    "city": "another random value",
                    "zip_code": zip_code,
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json()["message"] == "attempting to add duplicate address"

    def test_update_non_existant_address(self):

        response = self.api_client.put(
            reverse("get_and_update_address", kwargs={"address_id": uuid.UUID(int=1)}),
            data=json.dumps(
                {
                    "country": "GB",
                    "address_line_one": "address_line_one",
                    "address_line_two": "some random value",
                    "city": "another random value",
                    "zip_code": "TE1 1ST",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 404
        assert response.json()["message"] == "address not found"
