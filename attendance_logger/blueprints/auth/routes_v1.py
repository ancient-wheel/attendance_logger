import secrets
from flask.blueprints import Blueprint
from flask import request, current_app as app, url_for
import logging
from attendance_logger.models.database import db
from attendance_logger.models.db_models import EmailConfirmation, User
from attendance_logger.utils import utils, auth, communication
import datetime as dt
from attendance_logger.schemes import responses, auth_v1
from typing import Any
from flask_jwt_extended import jwt_required, current_user, create_access_token
from pydantic import ValidationError


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
auth_pb = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_pb.route("/register", methods=("POST",))
def register() -> tuple[dict, int]:
    try:
        form = auth_v1.Register.model_validate_json(request.get_data())
    except ValidationError:
        return (
            responses.BadRequestWithMessage(message="Missing fields.").model_dump(),
            400,
        )
    error_counter = 0
    response = responses.BadRequestWithMessages()
    # check username
    username = form.username
    if len(username) == 0:
        response.messages["username"] = "Username is required."
        error_counter += 1
    # check email
    email = form.email
    if not auth.validate_email(email, check_deliverability=True):
        response.messages["email"] = "Email failed validation."
        error_counter += 1
    else:
        email = email.lower()
        users = db.session.scalars(db.select(User).where(User.email == email)).all()
        if len(users) > 0:
            logger.warning("Registration attempts with existing email: %s", email)
            response.messages["email"] = "Email already registered."
            error_counter += 1
    # check password
    password = form.password
    if len(password) < 12 or len(password) > 128:
        response.messages["password"] = (
            "Password must contain at least of 12 and maximum 128 characters."
        )
        error_counter += 1
    if error_counter > 0:
        return response.model_dump(), 400
    with app.app_context():
        new_user = User(
            username=username,
            email=email,
            password=auth.hash_password(password),
            created_datetime=dt.datetime.now(dt.UTC),
            created_timezone=0,
        )
        db.session.add(new_user)
        db.session.commit()
        logger.info("New user registered: %s", email)
        request_confirmation(username=username, email=email)
    return responses.Ok().model_dump(), 200


_sentinel: Any = object()


@auth_pb.route("/confirmation", methods=("POST",))
def request_confirmation(
    username: str = _sentinel,
    email: str = _sentinel,
) -> tuple[dict, int]:
    try:
        form = auth_v1.Confirmation.model_validate_json(request.get_data())
    except ValidationError:
        if username is _sentinel or email is _sentinel:
            return (
                responses.BadRequestWithMessage(message="Missing fields.").model_dump(),
                400,
            )
    # check email
    email_ = email if email is not _sentinel else form.email
    if not auth.validate_email(email=email_, check_deliverability=False):
        logger.debug("request_confirm: Email failed validation.")
        return (
            responses.BadRequestWithMessage(
                message="Invalid credentials."
            ).model_dump(),
            400,
        )
    username_ = username if username is not _sentinel else form.username
    with app.app_context():
        # check user existance
        user = db.session.scalar(db.select(User).where(User.email == email_))
        if user is None:
            logger.debug("request_confirm: User doesn't exists.")
            return (
                responses.BadRequestWithMessage(
                    message="Invalid credentials."
                ).model_dump(),
                400,
            )
        # check email already confirmed
        if user.confirmed_at_utc is not None:
            return (
                responses.BadRequestWithMessage(
                    message="Email is already confirmed."
                ).model_dump(),
                400,
            )
        new_confirmation = EmailConfirmation(
            email=email_,
            token=secrets.token_urlsafe(32),
            created_datetime=dt.datetime.now(dt.UTC),
            created_timezone=0,
        )
        db.session.add(new_confirmation)
        db.session.commit()
        message = f"""
        Dear {username_},
        
        thank you for registering at our site. Please confirm your email by clicking the link below:
        {url_for('auth.confirm_email', token=new_confirmation.token, _external=True)}
        
        Best regards,
        Administration Team
        """
        communication.send_email(
            email_to=email_,
            subject="Email confirmation",
            body=message,
        )
    return responses.Ok().model_dump(), 200


@auth_pb.route("/token/<token>", methods=("GET",))
def confirm_email(token: str) -> tuple[dict, int]:
    with app.app_context():
        email_confirmation = db.session.scalar(
            db.select(EmailConfirmation).where(EmailConfirmation.token == token)
        )
        # check search result
        if not email_confirmation:
            logger.debug("Email confirmation token not found: %s", token)
            return (
                responses.BadRequestWithMessage(
                    message="Invalid or expired confirmation token"
                ).model_dump(),
                400,
            )
        # check token is already expired
        if (
            utils.convert_naive_time_to_aware(email_confirmation.expired_datetime_utc)
            < utils.get_current_utc_datetime()
        ):
            logger.debug("Email confirmation token expired: %s", token)
            return (
                responses.BadRequestWithMessage(
                    message="Invalid or expired confirmation token"
                ).model_dump(),
                400,
            )
        # check user existence
        user = db.session.scalar(
            db.select(User).where(User.email == email_confirmation.email)
        )
        if user is None:
            db.session.commit()
            logger.debug("Missing email for given token %s", token)
            return (
                responses.BadRequestWithMessage(
                    message="Invalid or expired confirmation token"
                ).model_dump(),
                400,
            )
        # check email is already confirmed
        if (
            email_confirmation.confirmed_at_utc is not None
            or user.confirmed_at_utc is not None
        ):
            if email_confirmation.confirmed_at_utc is None:
                email_confirmation.confirmed_at_utc = user.confirmed_at_utc
                email_confirmation.changed_at = utils.get_current_utc_datetime()
            elif user.confirmed_at_utc is None:
                user.confirmed_at_utc = email_confirmation.confirmed_at_utc
                user.changed_at = utils.get_current_utc_datetime()
            db.session.commit()
            return (
                responses.BadRequestWithMessage(
                    message="Email is already confirmed."
                ).model_dump(),
                400,
            )
        timestamp = utils.get_current_utc_datetime()
        email_confirmation.confirmed_at_utc = timestamp
        email_confirmation.changed_at = timestamp
        user.confirmed_at_utc = email_confirmation.confirmed_at_utc
        user.changed_at = utils.get_current_utc_datetime()
        db.session.commit()
        logger.info("User %s passed confirmation", user.email)
    return responses.Ok().model_dump(), 200


@auth_pb.route("/login", methods=("POST",))
def login() -> tuple[dict, int]:
    try:
        form = auth_v1.Login.model_validate_json(request.get_data())
    except ValidationError:
        return (
            responses.BadRequestWithMessage(message="Missing fields.").model_dump(),
            400,
        )
    # check email
    email = form.email
    if not auth.validate_email(email=email, check_deliverability=False):
        return (
            responses.BadRequestWithMessage(
                message="Invalid credentials."
            ).model_dump(),
            400,
        )
    email = email.lower()
    # check password
    password = form.password
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is None:
            logger.warning("User with email %s is not found", email)
            return (
                responses.BadRequestWithMessage(
                    message="Invalid credentials."
                ).model_dump(),
                400,
            )
        error_counter = 0
        if not auth.check_password_hash(password, user.password):
            logger.warning("Invalid password for user %s", user.email)
            error_counter += 1
        # check is user active
        if not user.is_active:
            logger.warning("User %s is deactivated.", user.email)
            error_counter += 1
        # check has user confirmed its email
        if user.confirmed_at_utc is None:
            logger.warning("Email for user %s is not confirmed.", user.email)
            error_counter += 1
        else:
            if (
                not utils.convert_naive_time_to_aware(user.confirmed_at_utc)
                < utils.get_current_utc_datetime()
            ):
                logger.warning(
                    "Confirmation time for user %s lay in future. Check database!!!"
                )
                error_counter += 1
        if error_counter > 0:
            return (
                responses.BadRequestWithMessage(
                    message="Invalid credentials."
                ).model_dump(),
                400,
            )
        logger.info("User %s logged in successfully", user.email)
        user.current_login_at = utils.get_current_utc_datetime()
        user.current_login_ip = request.remote_addr
        user.login_count += 1
        user.changed_at = utils.get_current_utc_datetime()
        db.session.commit()
        access_token = create_access_token(identity=user)
    return responses.OkAccessToken(access_token=access_token).model_dump(), 200


@auth_pb.route("/logout", methods=("GET",))
@jwt_required()
def logout() -> tuple[dict, int]:
    user = current_user
    user.last_login_at = user.current_login_at
    user.last_login_ip = user.current_login_ip
    db.session.commit()
    logger.info("User %s logged out successfully", current_user.email)
    return responses.Ok().model_dump(), 200
