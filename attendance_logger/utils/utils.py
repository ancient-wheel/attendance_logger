from flask import Request, current_app as app
from urllib.parse import urlsplit
import logging
import argon2
import datetime as dt
from email.policy import default as default_policy
import smtplib
from email.message import EmailMessage
import secrets
from werkzeug.datastructures import MultiDict

logger = logging.getLogger(__name__)


def get_next_page_secure(request: Request, fallback_url: str) -> str:
    """get argument next in request

    Method check if argument "next" exists and it's secure for redirection. Otherwise
    "fallback_url" is returned.

    Keyword arguments:
    request: flask.Request
    fallback_url: str
    Return: str representing safe url for redirection
    """

    next_page = request.args.get("next")
    if not next_page or urlsplit(next_page).netloc != "":
        next_page = fallback_url
    else:
        logger.warning("Parameter next in URL isn't relative. <next:%s>", next_page)
    return next_page


def check_password_hash(password: str, hashed: str) -> bool:
    """Check password against its hash

    Keyword arguments:
    password: str - plain text password
    hashed: str - hashed password
    Return: bool - True if password matches its hash, False otherwise
    """
    from argon2.exceptions import (
        VerifyMismatchError,
        InvalidHashError,
        VerificationError,
    )

    ph = argon2.PasswordHasher()
    try:
        ph.verify(hashed, password)
        return True
    except (VerifyMismatchError, InvalidHashError):
        return False
    except VerificationError as ve:
        logger.exception("Error during password verification: %s", ve)
        return False


def hash_password(password: str) -> str:
    """Hash password

    Keyword arguments:
    password: str - plain text password
    Return: str - hashed password
    """
    ph = argon2.PasswordHasher(
        memory_cost=65536,
        time_cost=3,
        parallelism=4,
        hash_len=32,
        salt_len=16,
        type=argon2.Type.ID,
    )
    return ph.hash(password)


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


def generate_contract_number(user_defined: str = "") -> str:
    """Generate a contract number

    The results start always with a year followed by slash and a unique combination
    of 8 ASCII digits.

    Keyword arguments:
    user_defined: str - user defined contract_number

    Return: str - unique contract number
    """
    if len(user_defined) > 0:
        return user_defined
    year = dt.date.today().year
    token = secrets.token_hex(4)
    return f"{year}/{token}"


def convert_native_time_to_aware(datetime: dt.datetime) -> dt.datetime:
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
