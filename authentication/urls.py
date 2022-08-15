from django.urls import path

from authentication.views import authenticate_user, logout_user

urlpatterns = [
    path("login/", authenticate_user, name="login_user"),
    path("logout/", logout_user, name="logout_user"),
]
