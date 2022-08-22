from flask import Flask, url_for, redirect
import os, logging
from mailer.initialization import AppIntializer
from flask_login import LoginManager

from mailer.models.ab_users import Users


def load_user(user_id):
    return Users.query.get(int(user_id))


def unauthorized_callback():
    "redirecting user to login page if un authenticated user trying to access secured pages."
    return redirect(url_for('users_view.login'))


def create_app():
    app = Flask(__name__)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(load_user) # Used to retrieve currently logged-in user object.
    login_manager.unauthorized_handler(unauthorized_callback) # send the user to login page.
    config_module = os.environ.get("APP_CONFIG", "mailer.config")
    app.config.from_object(config_module)
    intializer = AppIntializer(app)
    intializer.init_app()
    return app
