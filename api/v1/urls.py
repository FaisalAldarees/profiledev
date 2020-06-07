from django.urls import path

from api.v1.views import registration_views, login_views, edit_profile_views


app_name = "api"

urlpatterns = [
    path(
        "users/registration/",
        registration_views.CreateUserView.as_view(),
        name="registration",
    ),
    path('users/login/', login_views.CreateTokenView.as_view(), name='login'),
    path('users/avatar/', edit_profile_views.AvatarRetrieveUpdate.as_view(), name='avatar'),
]
