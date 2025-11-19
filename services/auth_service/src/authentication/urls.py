from django.urls import path

from api.auth import ConfirmView, LoginView

app_name = "authentication"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("confirm/", ConfirmView.as_view(), name="confirm"),
]

