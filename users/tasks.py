from celery.decorators import task
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from celery.task.schedules import crontab

from api.v1.utils import send_verification_email, delete_unverified_users, send_change_password

logger = get_task_logger(__name__)


@task(name="send_verification_email_task")
def send_verification_email_task(user_email):
    logger.info("Sent verification email")
    return send_verification_email(user_email)


@task(name="send_change_password")
def send_change_password_task(password_token):
    logger.info("Sent change password")
    return send_change_password(password_token)


@periodic_task(
    run_every=(crontab(hour='*/24')),
    name="delete_unverified_users",
    ignore_result=True
)
def delete_unverified_users_task():
    delete_unverified_users()
    logger.info("Users deleted")
