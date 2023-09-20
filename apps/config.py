import os

from apps.myconstant import *


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv("SECRET_KEY", "S#perS3crEt_007")

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    BROKER_URL = "redis://127.0.0.1:6379"
    CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379"

    # Assets Management
    ASSETS_ROOT = os.getenv("ASSETS_ROOT", "/static/assets")


class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(
        os.getenv("DB_ENGINE", "mysql"),
        os.getenv("DB_USERNAME", MDB_USERNAME),
        os.getenv("DB_PASS", MDB_PASSWORD),
        os.getenv("DB_HOST", "localhost"),
        os.getenv("DB_PORT", 3306),
        os.getenv("DB_NAME", "code_refactor_mmc"),
    )


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {"Production": ProductionConfig, "Debug": DebugConfig}
