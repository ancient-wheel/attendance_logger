from flask import Flask
import logging
from logging.config import dictConfig
from pathlib import Path
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

LOG_DIR_FILE_PATH = Path(__file__).parent.parent / "logs" / "flask.log"
LOG_DIR_FILE_PATH.parent.mkdir(exist_ok=True)
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            },
            "simple": {
                "format": "[%(asctime)s] %(levelname)s : %(message)s",
            },
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
                # 'formatter': 'simple',
            },
            "file-rotating": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": LOG_DIR_FILE_PATH,
                "mode": "a",
                "maxBytes": 1_000_000,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["wsgi", "file-rotating"],
        },
    }
)
logger = logging.getLogger(__name__)
migrate = Migrate()
jwt = JWTManager()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("attendance_logger.config.DevConfig")

    from attendance_logger.models.database import (
        db,
        init_db,
        add_roles,
        add_first_user_as_admin,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from attendance_logger.models.db_models import User

    @jwt.user_identity_loader
    def user_identity_lookup(user: User) -> str:
        """Register a callback function that takes whatever object is passed in as the
        identity when creating JWTs and converts it to a JSON serializable format.

        Keyword arguments:
        user: User - SQLAlchemy object representing user
        Return: int - identification of the user
        """

        return str(user.id_)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data) -> User:
        """Register a callback function that loads a user from your database whenever
        a protected route is accessed. This should return any python object on a
        successful lookup, or None if the lookup failed for any reason (for example
        if the user has been deleted from the database).

        Keyword arguments:
        argument -- description
        Return: return_description
        """

        identity = jwt_data["sub"]
        return db.session.scalar(db.select(User).where(User.id_ == identity))

    with app.app_context():
        init_db()
        add_roles()
        add_first_user_as_admin()

    from attendance_logger.blueprints.auth import routes_v1

    app.register_blueprint(routes_v1.auth_pb)

    return app
