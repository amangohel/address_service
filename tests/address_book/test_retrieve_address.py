import uuid

import pytest
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tests.factories import AddressBookFactory, UserFactory


class TestRetrieveAddress(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.login(username=cls.user.username, password="password")
        cls.token = Token.objects.create(user=cls.user)
        cls.api_client.credentials(HTTP_AUTHORIZATION="Token " + cls.token.key)

    def setUp(self):
        for _ in range(11):
            AddressBookFactory(
                user=self.user,
                country=self.fake.country(),
                address_line_one=self.fake.address(),
                city=self.fake.city(),
                zip_code=self.fake.postcode(),
            )

    @pytest.mark.django_db
    def test_get_single_address(self):

        AddressBookFactory(
            id=uuid.UUID(int=1),
            user=self.user,
            country="GB",
            address_line_one="1 Test Street",
            city="Test City",
            zip_code="TE1 1ST",
        )

        response = self.api_client.get(
            reverse(
                "get_and_update_address",
                kwargs={"address_id": "00000000-0000-0000-0000-000000000001"},
            )
        )
        data = response.json()

        assert data == {
            "id": "00000000-0000-0000-0000-000000000001",
            "country": "GB",
            "address_line_one": "1 Test Street",
            "address_line_two": None,
            "city": "Test City",
            "zip_code": "TE1 1ST",
        }

    @pytest.mark.django_db
    def test_get_single_address_does_not_exist(self):
        response = self.api_client.get(
            reverse(
                "get_and_update_address",
                kwargs={"address_id": "00000000-0000-0000-0000-000000000001"},
            )
        )
        data = response.json()

        assert data == {"message": "Address not found"}

    @pytest.mark.django_db
    def test_get_addresses_is_paginated(self):
        response = self.api_client.get(reverse("addresses"))
        assert response.json().get("count") == 11
        assert response.json().get("next") == "http://testserver/addresses/?page=2"
        assert response.json().get("previous") is None
        assert len(response.json().get("results")) == 10

        # Second request to call page 2 we assert the url for above
        response = self.api_client.get(reverse("addresses"), data={"page": 2})
        assert response.json().get("count") == 11
        assert response.json().get("next") is None
        assert response.json().get("previous") == "http://testserver/addresses/"
        assert len(response.json().get("results")) == 1
