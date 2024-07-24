"""Views."""

# external
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

# local
from ._utils import auth_required, expect_query_errors
from .actions import handle_query, handle_upload

views = Blueprint("views", __name__)


@views.route("/")
def home():
    """Home View."""
    return render_template("index.html", logged_in=current_user.is_authenticated)


@views.route("/upload", methods=["GET", "POST"])
@auth_required
def upload():
    """Upload View."""
    if request.method == "POST":
        if "file" in request.files:
            handle_upload.delay()
        return redirect(url_for("views.upload"))
    return render_template("actions/upload.html", logged_in=current_user.is_authenticated)


@views.route("/query", methods=["GET", "POST"])
@auth_required
@expect_query_errors
def query():
    """Upload View."""
    if request.method == "POST":
        query_field = request.form["query_field"]
        query_table = request.form["query_table"]
        query_condition = request.form["query_condition"]
        # TODO: proper input sanitization
        query_text = (
            f"SELECT {query_field or "*"} FROM {query_table}"
            + f"{' WHERE ' + query_condition if query_condition else '' };"
        )
        handle_query(query_text)
        return redirect(url_for("views.query"))
    return render_template("actions/query.html", logged_in=current_user.is_authenticated)


# --------------> error handlers <--------------


@views.errorhandler(413)
def _request_entity_too_large(error):
    # TODO: organize error handlers
    flash("File too large!", category="error")
    return redirect(url_for("views.upload"))
