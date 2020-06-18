from django.core.mail import EmailMessage
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


def send_verification_email(user_email_verification):
    email = EmailMessage(
        _("Verify your email"),
        "{0} {1}/v1/users/email_verification/{2}".format(
            _("Click to verify your email"), settings.HOST, user_email_verification.email_token
        ),
        to=[user_email_verification.user.email],
    )
    email.send()
    user_email_verification.created_at = timezone.now()
    user_email_verification.save()
