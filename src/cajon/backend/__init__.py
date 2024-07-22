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


def _create_db(app: Flask, db_path: Path):
    if db_path.exists() and db_path.is_file():
        return
    with app.app_context():
        db.create_all()


def _manage_session(app: Flask):
    login_manager = LoginManager()
    login_manager.login_view = "views.home"  # pyright: ignore[reportAttributeAccessIssue]
    login_manager.init_app(app)
    return login_manager


def create_app():
    """Create flask app."""
    cajon = Path(__file__).parent.parent  # cajon directory

    # app
    app = Flask(__name__, template_folder=cajon / "templates", static_folder=cajon / "static")
    app.config["SECRET_KEY"] = environ["SECRET_KEY"]  # expect KeyError
    # NOTE: os.urandom(24) is an alternative to static SECRET_KEY
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
    db_path = (cajon / "backend/database" / environ["DB_NAME"]).absolute()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    # expect KeyError & sqlalchemy.exc.NoSuchModuleError
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 * 1024  # 10 GB
    db.init_app(app)

    # local
    from ._utils import celery_init_app
    from .auth import auth
    from .models import User  # `db` must be defined before `User` is imported
    from .views import views

    # sub-apps
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # db, task, session
    _create_db(app, db_path)
    celery_init_app(app)
    lgm = _manage_session(app)

    @lgm.user_loader
    def _load_user(uid):
        # expect ValueError
        return User.query.get(int(uid))

    return app


__all__ = ("create_app", "db")
