"""Views."""

# external
from flask import Blueprint, render_template

views = Blueprint("views", __name__)


@views.route("/")
def home():
    """Home View."""
    return render_template("index.html")
