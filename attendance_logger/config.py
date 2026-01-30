import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv(dotenv_path="../.env")

"""Flask app configuration"""


# General Config
class Config:

    # Flask configuration
    SERVER_NAME = os.environ["SERVER_NAME"]
    SECRET_KEY = os.environ["SECRET_KEY"]

    # Flask JWT extended configuration
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

    # Email configuration
    EMAIL_SENDER = os.environ["EMAIL_SENDER"]
    EMAIL_SMTP_SERVER = os.environ["EMAIL_SMTP_SERVER"]
    EMAIL_SMTP_PORT = int(os.environ.get("EMAIL_SMTP_PORT"))
    EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]


class DevConfig(Config):
    """Set Flask config variables."""

    # Flask configuration
    APP_DEBUG = True

    # Flask-SQLALCHEMY
    # database configuration
    SQLALCHEMY_DATABASE_URI = os.environ["DB_URL"]

    APP_ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
    APP_ADMIN_DEFAULT_PASSWORD = os.environ["ADMIN_PASSWORD"]

    # Faker configuration
    FAKER_LOCALE = "ru_RU"


class ProdConfig(Config):
    pass
