import os
from celery.schedules import crontab
from mailer.views.base import base
from mailer.views.campaigns import campaigns
from mailer.views.security import users_view
from flask import session
from datetime import timedelta

BASEDIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = 'mysecret'
WHOOSH_BASE = 'whoosh'

"""############### cache config ################"""
CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_HOST": "localhost",
    "CACHE_REDIS_PORT": "6379",
    "CACHE_REDIS_DB": "0",
    "CACHE_REDIS_URL": "redis://redis:6379/0",
    "CACHE_DEFAULT_TIMEOUT": 500
}

"""############### Database config ################"""

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False

GMAIL_USER = 'myfirstmailerapp@gmail.com'
GMAIL_PASSWORD = 'tqrpsvtmdlehwbdf'

BLUEPRINTS = [base, campaigns, users_view]

"""############### celery config ################"""


class CeleryConfig:
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_LOG_LEVEL = "DEBUG"
    CELERY_IMPORTS = ("mailer.tasks.scheduler")
    CELERY_PREFETCH_MULTIPLIER = 1
    CELERYBEAT_SCHEDULE = {
        "email.scheduler": {
            "task": "email.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },

    }


CELERY_CONFIG = CeleryConfig

"""############### Session timeout config ################"""
PERMANENT_SESSION_LIFETIME = 1800
SESSION_REFRESH_EACH_REQUEST = True


def init_permanent_session(app):
    # automatic session timeout
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(seconds=PERMANENT_SESSION_LIFETIME)
        session.modified = True

    app.before_request(make_session_permanent)


FLASK_APP_MUTATOR = init_permanent_session

"""############### Commands used to run servers ################"""

"""
Run App: Flask run

Run celery beat: celery --app=mailer.tasks.celery_app:app beat

Run celery worker: celery --app=mailer.tasks.celery_app:app worker -O fair -l INFO

Run redis server: brew services restart redis >> Then >>  






"""
