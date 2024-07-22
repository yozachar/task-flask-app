"""Views."""

# standard
from datetime import datetime
from pathlib import Path

# external
from flask import Blueprint, flash, render_template, request
from flask_login import current_user
from werkzeug.utils import secure_filename

# local
from ._utils import auth_required

views = Blueprint("views", __name__)
ALLOWED_EXTENSIONS = ("CSV",)
UPLOAD_PATH = Path(__file__).parent / "database"


@views.route("/")
def home():
    """Home View."""
    return render_template("index.html", logged_in=current_user.is_authenticated)


@views.route("/upload", methods=["GET", "POST"])
@auth_required  # TODO: add HTTP redirect codes?
def upload():
    """Upload View."""
    if request.method == "POST":
        if "file" in request.files:
            _handle_upload()
    return render_template("actions/upload.html", logged_in=current_user.is_authenticated)


# --------------> accessory functions <--------------


def _handle_upload():
    uploaded_file = request.files["file"]
    filename = uploaded_file.filename
    if not filename:
        return False
    if (
        "." in filename
        and len(filename) < 3
        and filename.rsplit(".", 1)[1].upper() not in ALLOWED_EXTENSIONS
    ):
        return False
    s_file = secure_filename(filename).split(".", -1)[0] + " " + str(datetime.now()) + ".csv"
    uploaded_file.save(UPLOAD_PATH / s_file)
    flash("File uploaded.", category="success")
    return True
