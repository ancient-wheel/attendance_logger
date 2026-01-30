import logging
import smtplib
from email.message import EmailMessage
from email.policy import default as default_policy
from flask import current_app as app


logger = logging.getLoger(__name__)


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
