"""Views."""

# external
from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint("views", __name__)


@views.route("/")
def home():
    """Home View."""
    return render_template("index.html", logged_in=current_user.is_authenticated)
