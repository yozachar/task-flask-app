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
    project = Path(__file__).parent.parent

    # app
    app = Flask(__name__, template_folder=project / "templates", static_folder=project / "static")
    app.config["SECRET_KEY"] = environ["SECRET_KEY"]  # expect KeyError

    # database
    db_path = (project / "backend/database" / environ["DB_NAME"]).absolute()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    # expect KeyError & sqlalchemy.exc.NoSuchModuleError
    db.init_app(app)

    # local
    from .auth import auth
    from .models import User  # `db` must be defined before `User` is imported
    from .views import views

    # sub-apps
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    _create_db(app, db_path)
    lgm = _manage_session(app)

    @lgm.user_loader
    def _load_user(uid):
        # expect ValueError
        return User.query.get(int(uid))

    return app


__all__ = ("create_app", "db")
