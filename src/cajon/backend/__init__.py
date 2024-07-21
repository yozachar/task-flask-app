"""Backend."""

# standard
from os import environ
from pathlib import Path

# external
from dotenv import load_dotenv
from flask import Flask


def create_app():
    """Create flask app."""
    load_dotenv()
    project = Path(__file__).parent.parent
    app = Flask(__name__, template_folder=project / "templates", static_folder=project / "static")
    app.config["SECRET_KEY"] = environ["SECRET_KEY"]  # expect KeyError

    # local
    from .views import views

    app.register_blueprint(views, url_prefix="/")

    return app


__all__ = ("create_app",)
