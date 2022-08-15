from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password"]

    def save(self):
        user = User(email=self.validated_data["email"])
        user.set_password(self.validated_data["password"])
        user.save()
        return user
