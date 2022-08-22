from mailer.extensions import db, migrate, APP_DIR, cache, celery_app
from flask_login import LoginManager
import logging


class AppIntializer:

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config = app.config

    def init_app(self):
        self.setup_db()
        self.register_blueprints()
        self.configure_cache()
        self.configure_logging()
        self.configure_celery()
        with self.app.app_context():
            self.init_app_in_ctx()

    def configure_celery(self) -> None:
        celery_app.config_from_object(self.config["CELERY_CONFIG"])
        celery_app.set_default()
        mailer_app = self.app

        # Here, we want to ensure that every call into Celery task has an app context
        # setup properly
        task_base = celery_app.Task

        class AppContextTask(task_base):  # type: ignore
            # pylint: disable=too-few-public-methods
            abstract = True

            # Grab each call into the task and set up an app context
            def __call__(self, *args, **kwargs):
                with mailer_app.app_context():
                    return task_base.__call__(self, *args, **kwargs)

        celery_app.Task = AppContextTask

    def setup_db(self):
        db.init_app(self.app) # Initializing Database object.
        migrate.init_app(self.app, db=db, directory=APP_DIR + "/migrations") # Initializing Migration object

    def register_blueprints(self):
        for bp in self.config["BLUEPRINTS"]:
            self.app.register_blueprint(bp) # registering blueprint for making URls.

    def configure_cache(self):
        cache_config = self.config.get("CACHE_CONFIG")
        cache.init_app(self.app, cache_config) # Initializing cache object

    def configure_logging(self):
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s-%(levelname)s-%(message)s")

    def init_app_in_ctx(self) -> None:
        """
        Runs init logic in the context of the app
        """

        # Hook that provides administrators a handle on the Flask APP
        # after initialization
        flask_app_mutator = self.config["FLASK_APP_MUTATOR"]
        if flask_app_mutator:
            flask_app_mutator(self.app)