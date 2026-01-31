from functools import wraps
from typing import Any
from flask_jwt_extended import jwt_required, get_jwt
from attendance_logger.schemes import responses
from collections.abc import Callable


def roles_required(*roles, optional: bool = False) -> Callable:
    """A decorator to restrict protected endpoints with certain user roles stored
    in the token. Roles "admin" and "owner" don't require to be explicite meansioned.

    Keyword arguments:
    roles: list[str] - list of accepted user roles,
    optional: bool - same as flask_jwt_extended(optional)

    Return: Callable
    """

    def decorator(func) -> Callable:
        @wraps(func)
        @jwt_required(optional=optional)
        def decorated_function(*args, **kwargs) -> Any:
            claims = get_jwt()["roles"]
            roles_ = list(roles)
            roles_.extend(("admin", "owner"))
            roles_ = frozenset(roles_)
            check_roles = [role for role in claims if role in roles_]
            if not optional and len(check_roles) == 0:
                return responses.Forbidden().model_dump(), 403
            return func(*args, **kwargs)

        return decorated_function

    return decorator
