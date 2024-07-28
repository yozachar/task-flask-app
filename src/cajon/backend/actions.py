"""Upload task."""

# standard
from datetime import datetime

# external
from flask import flash, request
from sqlalchemy import text
from werkzeug.utils import secure_filename

# local
from . import cajon, db
from .transactions import action

ALLOWED_EXTENSIONS = ("CSV",)
UPLOAD_FOLDER = cajon / "backend/uploads"
if not UPLOAD_FOLDER.exists():
    UPLOAD_FOLDER.mkdir(parents=True)


def handle_upload():
    """Handle upload."""
    r_file = request.files["file"]
    filename = r_file.filename

    if not filename or (
        r_file.mimetype != "text/csv"
        or "." not in filename
        or len(filename) < 3
        or filename.rsplit(".", 1)[1].upper() not in ALLOWED_EXTENSIONS
    ):
        flash("Invalid file or filename.", category="error")
        return

    s_file = secure_filename(filename).split(".", -1)[0] + " " + str(datetime.now()) + ".csv"
    chunk_size = 1024**2  # 1MB
    uploaded_file = UPLOAD_FOLDER / s_file
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
    action.delay(str(uploaded_file.absolute()), s_file)
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
