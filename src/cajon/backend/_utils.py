"""Utils."""

# standard
from functools import wraps

# external
from celery import Celery, Task
from flask import Flask, flash, redirect, url_for
from flask_login import current_user


def auth_required(func):
    """Check authentication."""

    @wraps(func)
    def _decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please first login.", category="warning")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return _decorated_function


def authenticated(func):
    """Check authentication."""

    @wraps(func)
    def _decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("Already Signed In!", category="success")
            return redirect(url_for("views.home"))
        return func(*args, **kwargs)

    return _decorated_function


def celery_init_app(app: Flask) -> Celery:
    """Celery Init App."""
    # https://flask.palletsprojects.com/en/2.2.x/patterns/celery/

    class FlaskTask(Task):
        """Flask Task."""

        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
