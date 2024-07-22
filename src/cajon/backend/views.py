"""Views."""

# external
from flask import Blueprint, render_template
from flask_login import current_user, login_required  # type: ignore

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    """Home View."""
    return render_template("index.html", is_logged_in=current_user.authenticated)
