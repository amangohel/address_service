from datetime import timedelta

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authentication.serializers import UserSerializer


def token_expire_handler(token):
    """Check the assigned token is expired or not"""
    time_elapsed = timezone.now() - token.created
    remaining_time = timedelta(seconds=settings.TOKEN_EXPIRATION_TIME) - time_elapsed
    is_expired = remaining_time < timedelta(seconds=0)
    if is_expired:
        token.delete()
        token = Token.objects.create(user=token.user)
    return is_expired, token


@api_view(["POST"])
@permission_classes([AllowAny])
@swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["username", "password"],
    ),
    responses={201: "Returns a token", 404: "No such user exists", 401: "invalid credentials"},
)
def authenticate_user(request):
    """
    Authenticate a user and return an authentication token
    """
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = User.objects.get(email=serializer.data["email"])
    except User.DoesNotExist:
        raise AuthenticationFailed("No such user exists", 404)
    if not check_password(serializer.data["password"], user.password):
        raise AuthenticationFailed("Invalid credentials", 400)
    token, _ = Token.objects.get_or_create(user=user)
    is_expired, token = token_expire_handler(token)
    if is_expired:
        token = Token.objects.create(user=user)
    login(request, user)
    return Response({"token": token.key}, 201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout a user and delete the token
    """
    Token.objects.get(user=request.user).delete()
    logout(request)
    return Response({"message": "Logged out successfully"}, 200)
