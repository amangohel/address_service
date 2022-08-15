import json

from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tests.factories import AddressBookFactory, UserFactory


class TestCreateAddress(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.login(username=cls.user.username, password="password")
        cls.token = Token.objects.create(user=cls.user)
        cls.api_client.credentials(HTTP_AUTHORIZATION="Token " + cls.token.key)

    def test_create_address(self):
        response = self.api_client.post(
            reverse("addresses"),
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

    def test_create_address_fails_if_missing_inputs(self):
        response = self.api_client.post(
            reverse("addresses"),
            data=json.dumps(
                {
                    "country": "US",
                    "address_line_one": "1 Testerson Street",
                    "address_line_two": "Test Town",
                    "city": "Bean City",
                    "zip_code": "",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json() == {"zip_code": ["This field may not be blank."]}

    def test_create_address_fails_if_invalid_country(self):
        response = self.api_client.post(
            reverse("addresses"),
            data=json.dumps(
                {
                    "country": "JA",  # JA is a invalid country
                    "address_line_one": "1 Testerson Street",
                    "address_line_two": "Test Town",
                    "city": "Bean City",
                    "zip_code": "TE1 1ST",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json() == {"non_field_errors": ["Country is not valid"]}

    def test_create_address_fails_if_invalid_address_line_one(self):
        response = self.api_client.post(
            reverse("addresses"),
            data=json.dumps(
                {
                    "country": "GB",
                    "address_line_one": "testtesttesttesttesttesttesttesttesttesttesttesttes",
                    "address_line_two": "Test Town",
                    "city": "Bean City",
                    "zip_code": "TE1 1ST",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json() == {
            "address_line_one": ["Ensure this field has no more than 50 characters."]
        }

    def test_create_address_fails_if_invalid_address_line_two(self):
        response = self.api_client.post(
            reverse("addresses"),
            data=json.dumps(
                {
                    "country": "GB",
                    "address_line_one": "1 Testerson Street",
                    "address_line_two": "testtesttesttesttesttesttesttesttesttesttesttesttes",
                    "city": "Bean City",
                    "zip_code": "TE1 1ST",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json() == {
            "address_line_two": ["Ensure this field has no more than 50 characters."]
        }

    def test_create_address_fails_if_invalid_city(self):
        response = self.api_client.post(
            reverse("addresses"),
            data=json.dumps(
                {
                    "country": "JA",  # JA is a invalid country
                    "address_line_one": "1 Testerson Street",
                    "address_line_two": "Test Town",
                    "city": "testtesttesttesttesttesttesttesttesttesttesttesttes",
                    "zip_code": "TE1 1ST",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json() == {"city": ["Ensure this field has no more than 50 characters."]}

    def test_create_fails_if_existing_address(self):
        # Address line one and zip code are composed together
        # to uniquely identify an address
        address_line_one = "1 Test Street"
        zip_code = "TE1 1ST"

        AddressBookFactory(
            user=self.user,
            country="GB",
            address_line_one=address_line_one,
            address_line_two="address_line_two",
            city="city",
            zip_code=zip_code,
        )

        response = self.api_client.post(
            reverse("addresses"),
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
