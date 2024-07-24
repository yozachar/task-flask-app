"""Upload task."""

# standard
from datetime import datetime

# external
from celery import shared_task
from flask import flash, request
from sqlalchemy import text
from werkzeug.utils import secure_filename

# local
from . import cajon, db
from .transactions import action

ALLOWED_EXTENSIONS = ("CSV",)
UPLOAD_PATH = cajon / "backend/uploads"
if not UPLOAD_PATH.exists():
    UPLOAD_PATH.mkdir(parents=True)


@shared_task
def handle_upload():
    """Handle upload."""
    r_file = request.files["file"]
    filename = r_file.filename

    if not filename or (
        "." not in filename
        or len(filename) < 3
        or filename.rsplit(".", 1)[1].upper() not in ALLOWED_EXTENSIONS
    ):
        flash("Invalid file or filename.", category="error")
        return

    s_file = secure_filename(filename).split(".", -1)[0] + " " + str(datetime.now()) + ".csv"
    chunk_size = 1024**2  # 1MB
    uploaded_file = UPLOAD_PATH / s_file
    flash("Uploading file ...", category="info")
    with uploaded_file.open("wb") as buf:
        while len(each_chunk := r_file.stream.read(chunk_size)) > 0:
            buf.write(each_chunk)

    if uploaded_file.stat().st_size == 0:
        flash("File is empty. Please try again.", category="error")
        uploaded_file.unlink()
        return
    flash("File uploaded.", category="success")

    flash("Writing file to DB ...", category="info")
    action(uploaded_file, s_file)
    flash("File written to DB.", category="success")
    uploaded_file.unlink()  # comment to verify


def handle_query(query_text):
    """Handle Query."""
    with db.engine.connect() as conn:
        result = conn.execute(text(query_text))
        rc = result.rowcount
    # SELECT * FROM user;
    # SELECT * FROM product_data WHERE price > 20;
    flash(f"{rc} record{'' if rc == 1 else 's'} found.", category="info")
