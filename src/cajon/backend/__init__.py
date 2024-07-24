"""Backend."""

# standard
from os import environ
from pathlib import Path

# external
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
db = SQLAlchemy()
cajon = Path(__file__).parent.parent


def get_pg_uri(use_psycopg: bool = False):
    """Postgres connection URI."""
    # expect KeyError
    _pg_user = environ["POSTGRES_USER"]
    _pg_passwd = environ["POSTGRES_PASSWORD"]
    _db_host = environ["PG_DB_HOST"]
    _db_port = environ["PG_DB_PORT"]
    _db_name = environ["POSTGRES_DB"]
    return (
        f"postgresql{'+psycopg' if use_psycopg else ''}://"
        + f"{_pg_user}:{_pg_passwd}@{_db_host}:{_db_port}/{_db_name}"
    )


def _manage_session(app: Flask):
    login_manager = LoginManager()
    login_manager.login_view = "views.home"  # pyright: ignore[reportAttributeAccessIssue]
    login_manager.init_app(app)
    return login_manager


def _config_flask(app: Flask):
    app.config["SECRET_KEY"] = environ["SECRET_KEY"]  # expect KeyError
    # NOTE: os.urandom(Integer) is an alternative to static SECRET_KEY
    # TODO: provide config for UPLOAD_FOLDER
    app.config["UPLOAD_FOLDER"] = cajon / "backend/uploads"

    # celery
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()

    # database
    app.config["SQLALCHEMY_DATABASE_URI"] = get_pg_uri(use_psycopg=True)
    # expect KeyError & sqlalchemy.exc.NoSuchModuleError
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 * 1024  # 10 GB


def _peripherals(app: Flask):
    # initialize app for use with SQLAlchemy ORM
    db.init_app(app)

    # local imports
    from ._utils import celery_init_app
    from .auth import auth
    from .models import User  # `db` must be defined before `User` is imported
    from .views import views

    # blueprints
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # db, task, session
    with app.app_context():
        db.create_all()
    celery_init_app(app)
    lgm = _manage_session(app)

    @lgm.user_loader
    def _load_user(uid):
        # expect ValueError
        return User.query.get(int(uid))


def create_app():
    """Create flask app."""
    app = Flask(__name__, template_folder=cajon / "templates", static_folder=cajon / "static")
    _config_flask(app)
    _peripherals(app)
    return app


__all__ = ("create_app", "db", "cajon", "get_pg_uri")
