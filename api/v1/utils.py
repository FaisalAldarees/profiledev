from django.core.mail import EmailMessage
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

import requests


def send_verification_email(user_email):
    user_email_verification = get_user_model().objects.get(email=user_email).user_email_verification

    email = EmailMessage(
        _("Verify your email"),
        "{0} {1}/v1/users/verification/{2}".format(
            _("Click to verify your email"), settings.HOST, user_email_verification.email_token
        ),
        to=[user_email],
    )
    email.send()
    user_email_verification.created_at = timezone.now()
    user_email_verification.save()
    return user_email


def send_change_password(user_email):
    user = get_user_model().objects.get(email=user_email)

    email = EmailMessage(
        _("Password Change"),
        "{0} {1}/v1/users/password/change/{2}".format(
            _("Click to change your password"), settings.HOST, user.password_token
        ),
        to=[user_email],
    )
    email.send()


def delete_unverified_users():
    users = get_user_model().objects.filter(is_email_verified=False)

    for user in users:
        user.delete()


def verifiy_recaptcha(token):
    res = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", {"secret": settings.RECAPTCHA_SECRET_KEY, "response": token}
    )
    return res.json()["success"]
