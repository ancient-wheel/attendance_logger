from flask import current_app as app
import logging
import datetime as dt
from email.policy import default as default_policy
import smtplib
from email.message import EmailMessage
from werkzeug.datastructures import MultiDict


logger = logging.getLogger(__name__)


def get_current_utc_datetime() -> dt.datetime:
    """Get current UTC time

    Return: dt.datetime - current UTC time
    """
    return dt.datetime.now(dt.UTC)


def get_current_utc_datetime_plus_hours(hours: int) -> dt.datetime:
    """Get current UTC time plus specified hours

    Keyword arguments:
    hours: int - number of hours to add to current UTC time
    Return: dt.datetime - current UTC time plus specified hours
    """
    return dt.datetime.now(dt.UTC) + dt.timedelta(hours=hours)


def send_email(email_to: str, subject: str, body: str) -> None:
    """Send email (stub function)

    Keyword arguments:
    email_to: str - recipient email address
    subject: str - email subject
    body: str - email body
    """
    logger.info("Sending email to %s with subject '%s'", email_to, subject)
    msg = EmailMessage(policy=default_policy)
    msg["Subject"] = subject
    msg["From"] = app.config.get("EMAIL_SENDER")
    msg["To"] = email_to
    msg.set_content(body)

    with smtplib.SMTP_SSL(
        app.config.get("EMAIL_SMTP_SERVER", app.config.get("EMAIL_SMTP_PORT"))
    ) as smtp:
        smtp.login(app.config.get("EMAIL_SENDER"), app.config.get("EMAIL_PASSWORD"))
        smtp.send_message(msg)

    logger.info("Email sent to %s with subject %s", email_to, subject)


def convert_naive_time_to_aware(datetime: dt.datetime) -> dt.datetime:
    """Convert datetime in native format into aware format by setting timezone
    to UTC timezone.

    Keyword arguments:
    datetime: datetime.datetime - object to modify
    Return: datetime.datetime
    """

    return datetime.replace(tzinfo=dt.UTC)


def extract_offset_limit(request_args: MultiDict) -> tuple[int, int]:
    """Check for parameters for paging parameters for optimal database performance

    Keyword arguments:
    request_args: MultiDict - result of flask.request.args

    Return: tuple[int, int] - (offset, limit)
    if offset=-1 paging is not set
    """

    page = request_args.get("page", -1)
    items_per_page = request_args.get("limit", 20)
    offset_items = (page - 1) * items_per_page
    limit_items = offset_items = items_per_page
    return (offset_items, limit_items)
