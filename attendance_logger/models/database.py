from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
import logging
import datetime as dt


logger = logging.getLogger(__name__)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)
Base = declarative_base()
db = SQLAlchemy(model_class=Base, metadata=metadata)


def init_db() -> None:
    from attendance_logger.models.db_models import (
        User,
        UserRole,
        Client,
        Contract,
        Group,
        Lesson,
        Price,
        Subscription,
        Schedule,
        Location,
        UserParticipant,
        ClientParticipant,
        Favorites,
    )

    db.create_all()
    logger.debug("Created DB tables")


def add_roles():
    from attendance_logger.models.db_models import UserRole
    from attendance_logger.models.models import UserRoles

    with app.app_context():
        roles = []
        if (
            db.session.scalar(
                db.select(UserRole).where(UserRole.name == UserRoles.USER.value)
            )
            is None
        ):
            roles.append(
                UserRole(
                    name=UserRoles.USER.value,
                    description="Regular user with limited access",
                )
            )
        if (
            db.session.scalar(
                db.select(UserRole).where(UserRole.name == UserRoles.EMPLOYEE.value)
            )
            is None
        ):
            roles.append(
                UserRole(
                    name=UserRoles.EMPLOYEE.value,
                    description="Employee with limited access",
                )
            )
        if (
            db.session.scalar(
                db.select(UserRole).where(UserRole.name == UserRoles.MANAGER.value)
            )
            is None
        ):
            roles.append(
                UserRole(
                    name=UserRoles.MANAGER.value,
                    description="Manager with elevated access",
                )
            )
        if (
            db.session.scalar(
                db.select(UserRole).where(UserRole.name == UserRoles.HEAD_MANAGER.value)
            )
            is None
        ):
            roles.append(
                UserRole(
                    name=UserRoles.HEAD_MANAGER.value,
                    description="Head Manager with broad access",
                )
            )
        if (
            db.session.scalar(
                db.select(UserRole).where(UserRole.name == UserRoles.OWNER.value)
            )
            is None
        ):
            roles.append(
                UserRole(
                    name=UserRoles.OWNER.value,
                    description="Owner of the service with full access",
                )
            )
        if (
            db.session.scalar(
                db.select(UserRole).where(UserRole.name == UserRoles.ADMIN.value)
            )
            is None
        ):
            roles.append(
                UserRole(
                    name=UserRoles.ADMIN.value,
                    description="Administrator with full access",
                )
            )
        if roles:
            db.session.add_all(roles)
            db.session.commit()
            logger.debug("Added missing roles to the database")
        else:
            logger.debug("All roles already exist in the database")


def add_first_user_as_admin():
    from attendance_logger.models.db_models import User, UserRole
    from attendance_logger.utils.auth import hash_password

    with app.app_context():
        if db.session.get(User, 1) is None:
            logger.info("List of users is empty. Adding first user.")
            data = app.config.get_namespace("APP_ADMIN")
            admin = User(
                username="admin",
                email=data["_email"],
                password=hash_password(data["_default_password"]),
                created_datetime=dt.datetime.now(dt.UTC),
                created_timezone=0,
                confirmed_at_utc=dt.datetime.now(dt.UTC),
            )
            admin_role = db.session.scalar(db.select(UserRole).where(UserRole.name == "admin"))
            admin.roles.append(admin_role)
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin is added to user's list.")
