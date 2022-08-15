from django.urls import path

from address_book.views import AddressAPI as AddressBookView
from address_book.views import GetAndUpdateAddressView

urlpatterns = [
    path("", AddressBookView.as_view(), name="addresses"),
    path(
        "<uuid:address_id>/",
        GetAndUpdateAddressView.as_view(http_method_names=["put", "get"]),
        name="get_and_update_address",
    ),
]
