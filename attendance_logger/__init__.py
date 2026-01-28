from flask import Flask
import logging
from logging.config import dictConfig
from pathlib import Path
from flask_migrate import Migrate
from flask_login import LoginManager


LOG_DIR_FILE_PATH = Path(__file__).parent / "logs" / "flask.log"
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
login_manager = LoginManager()


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
    login_manager.init_app(app)

    with app.app_context():
        init_db()
        add_roles()
        add_first_user_as_admin()

    from attendance_logger.blueprints.main.routes_v1 import main_pb
    from attendance_logger.blueprints.auth.routes_v1 import auth_pb

    app.register_blueprint(main_pb, url_prefix="/api/v1")
    app.register_blueprint(auth_pb, url_prefix="/api/v1")

    return app
