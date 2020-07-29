from django.urls import path

from api.v1.views import (
    registration_views,
    login_views,
    edit_profile_views,
    email_verification_views,
    search_views,
    password_views,
)


app_name = "api"

urlpatterns = [
    path("users/registration/", registration_views.CreateUserView.as_view(), name="registration",),
    path("users/login/", login_views.CreateTokenView.as_view(), name="login"),
    path("users/avatar/", edit_profile_views.AvatarUpdate.as_view(), name="avatar_update",),
    path("users/<int:user_id>/avatar/", edit_profile_views.AvatarRetrieve.as_view(), name="avatar_retrive",),
    path("users/profile/", edit_profile_views.UserProfileUpdate.as_view(), name="profile_update",),
    path("users/<int:user_id>/profile/", edit_profile_views.UserProfileRetrive.as_view(), name="profile_retrive",),
    path(
        "users/email/verification/<str:email_token>/",
        email_verification_views.VerifyEmail.as_view(),
        name="email_verification",
    ),
    path(
        "users/email/send_verification/",
        email_verification_views.ResendEmail.as_view(),
        name="resend_email_verification",
    ),
    path("users/search/", search_views.UserSearchList.as_view(), name="search"),
    path(
        "users/password/change/<str:password_token>/", password_views.ChangePassword.as_view(), name="change_password"
    ),
    path(
        "users/password/send_link/",
        password_views.SendChangePasswordLink.as_view(),
        name="send_change_password_link",
    ),
]
