import os
from importlib import import_module

from celery import Celery
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy

from apps.myconstant import *

db = SQLAlchemy()
db2 = PyMongo()
login_manager = LoginManager()
celery = Celery()

from apps.config import config_dict

# WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

# The configuration
get_config_mode = "Debug" if DEBUG else "Production"

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit("Error: Invalid <config_mode>. Expected values [Debug, Production] ")


def create_app():
    app = Flask(__name__)
    import os

    SECRET_KEY = os.urandom(32)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    configure_celery(app)
    mongo_config(app)
    app.app_context().push()
    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ("authentication", "home"):
        module = import_module("apps.{}.routes".format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def configure_celery(app=None):
    app = app or create_app()
    app.config["BROKER_URL"] = "redis://127.0.0.1:6379"
    app.config["CELERY_RESULT_BACKEND"] = "redis://127.0.0.1:6379"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://" + MDB_USERNAME + ":" + MDB_PASSWORD + "@localhost:3306/xero_to_qbo"
    )
    app.config["MONGO_URI"] = "mongodb://localhost:27017/xero_to_qbo"

    # for conf in config_dict[get_config_mode.capitalize()]:
    #     print(conf)
    celery.conf.update(app.config)
    return celery


def mongo_config(app=None):
    mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/MMC")
    db2 = mongodb_client.db
    return db2
