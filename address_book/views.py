import json
import uuid

from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from address_book.models import AddressBook
from address_book.serializer import AddressBookSerializer


class GetAndUpdateAddressView(APIView):
    @swagger_auto_schema(responses={200: AddressBookSerializer(many=False), 404: "Not found"})
    def get(self, request, address_id=None) -> Response:
        """
        Get an address under a specific ID
        """
        user = User.objects.get(email=request.user.email)
        if address_id:
            try:
                serializer = AddressBookSerializer(user.addresses.get(id=address_id))
            except AddressBook.DoesNotExist:
                return Response({"message": "Address not found"}, status=404)
            return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "address_line_one": openapi.Schema(type=openapi.TYPE_STRING),
                "address_line_two": openapi.Schema(type=openapi.TYPE_STRING),
                "city": openapi.Schema(type=openapi.TYPE_STRING),
                "zip_code": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["country", "address_line_one", "zip_code", "city"],
            additional_properties=["address_line_two"],
        ),
        responses={200: AddressBookSerializer(many=False), 404: "Address not found"},
        operation_description="Update an address in the address book",
    )
    def put(self, request, address_id=None) -> Response:
        """
        Update an address in the address book.

        Assumptions
        An assumption I made here was that a user, for a specific address,
        would click an update button on the client side and the client would
        send the ID of the address to update
        """
        user = User.objects.get(email=request.user.email)
        address_data = json.loads(request.body)

        serializer = AddressBookSerializer(data=address_data)
        serializer.is_valid(raise_exception=True)

        if AddressBookSerializer.address_exists_for_user(
            user,
            serializer.data.get("address_line_one"),
            serializer.data.get("zip_code"),
        ):
            return Response({"message": "attempting to add duplicate address"}, status=400)

        if serializer.data:
            try:
                address = user.addresses.get(id=address_id)
            except AddressBook.DoesNotExist:
                return Response({"message": "address not found"}, status=404)
            serializer.update(address, serializer.data)
            return Response(serializer.data, status=200)


class AddressAPI(APIView, PageNumberPagination):
    authentication_classes = [TokenAuthentication]
    pagination_class = PageNumberPagination
    page_size = 10
    max_page_size = 100

    @swagger_auto_schema(
        responses={200: AddressBookSerializer(many=True), 400: "Failed to create address"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["country", "address_line_one", "zip_code", "city"],
            additional_properties=["address_line_two"],
            properties={
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "address_line_one": openapi.Schema(type=openapi.TYPE_STRING),
                "address_line_two": openapi.Schema(type=openapi.TYPE_STRING),
                "city": openapi.Schema(type=openapi.TYPE_STRING),
                "zip_code": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        operation_description="Create an address",
    )
    def post(self, request) -> Response:
        """
        Add a new address to the address book.
        """
        user = User.objects.get(email=request.user.email)
        serializer = AddressBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.data:
            if AddressBookSerializer.address_exists_for_user(
                user,
                serializer.data.get("address_line_one"),
                serializer.data.get("zip_code"),
            ):
                return Response(
                    {"message": "attempting to add duplicate address"},
                    status=400,
                )
            AddressBookSerializer.create(self, {"user": user, **serializer.data})
            return Response(serializer.data, status=200)

        return Response({"Failed to create address"}, status=400)

    @swagger_auto_schema(responses={200: AddressBookSerializer(many=True)})
    def get(
        self,
        request,
    ) -> Response:
        """
        Get all addresses for a user
        """
        user = User.objects.get(email=request.user.email)

        addresses = user.addresses.select_related("user")
        page = self.paginate_queryset(addresses, request=request)
        if page is not None:
            serializer = AddressBookSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "address_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)
                ),
            },
            required=["address_ids"],
        ),
        responses={204: "Successfully deleted addresses"},
        operation_description="Delete an address from an address book",
    )
    def delete(self, request) -> Response:
        """
        Delete address(es) from the address book
        """
        user = User.objects.get(email=request.user.email)
        ids = [uuid.UUID(id) for id in request.data["address_ids"]]
        addresses_to_delete = user.addresses.filter(id__in=ids)

        if len(addresses_to_delete) > 0:
            addresses_to_delete.delete()
            return Response(status=204)
