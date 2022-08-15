import uuid

from django.contrib.auth.models import User
from django.db import models


class AddressBook(models.Model):
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    country = models.CharField(max_length=2)
    address_line_one = models.CharField(max_length=50)
    address_line_two = models.CharField(max_length=50, null=True, blank=True)  # optional
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.address_line_one}, {self.city} {self.zip_code}"
