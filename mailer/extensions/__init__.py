from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os,celery
from celery import Celery
from flask_caching import Cache

APP_DIR = os.path.join(os.path.dirname(__file__), os.path.pardir)
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
celery_app = Celery()