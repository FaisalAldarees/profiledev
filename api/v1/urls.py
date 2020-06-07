from django.urls import path

from api.v1.views import registration_views


app_name = "api"

urlpatterns = [
    path(
        "users/registration/",
        registration_views.CreateUserView.as_view(),
        name="registration",
    ),
]
