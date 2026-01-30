import argon2
import logging

import email_validator

logger = logging.getLogger(__name__)


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


def validate_email(email: str, check_deliverability: bool = False) -> bool:
    try:
        email_validator.validate_email(email, check_deliverability=check_deliverability)
    except email_validator.EmailNotValidError:
        return False
    else:
        return True
