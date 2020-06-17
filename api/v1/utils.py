from django.core.mail import EmailMessage
from django.utils import timezone
from django.conf import settings


def send_verification_email(user_email_verification):
    email = EmailMessage(
        "Verify your email",
        "Click the link to verifiy your email {0}/v1/users/email_verification/{1}".format(
            settings.HOST, user_email_verification.email_token
        ),
        to=[user_email_verification.user.email],
    )
    email.send()
    user_email_verification.created_at = timezone.now()
    user_email_verification.save()
