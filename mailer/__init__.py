from flask import current_app, Flask
from mailer.extensions import db
from mailer.server import create_app

app: Flask = current_app
