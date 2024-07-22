"""Utils."""

# standard
from functools import wraps

# external
from flask import flash, redirect, url_for
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
