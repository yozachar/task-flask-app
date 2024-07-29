"""Upload task."""

# standard
from datetime import datetime

# external
from flask import flash, request
from sqlalchemy import text
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# local
from . import cajon, db
from .transactions import action

ALLOWED_EXTENSIONS = ("CSV",)
UPLOAD_FOLDER = cajon / "backend/uploads"
if not UPLOAD_FOLDER.exists():
    UPLOAD_FOLDER.mkdir(parents=True)


def _check_file(name: str | None, mime: str):
    if not name or (
        mime != "text/csv"
        or "." not in name
        or len(name) < 3
        or name.rsplit(".", 1)[1].upper() not in ALLOWED_EXTENSIONS
    ):
        flash("Invalid file or filename.", category="error")
        return
    return secure_filename(name).split(".", -1)[0] + " " + str(datetime.now()) + ".csv"


def _upload_file(name: str, store: FileStorage):
    chunk_size = 1024**2  # 1MB
    u_file = UPLOAD_FOLDER / name
    flash("Uploading file ...", category="info")
    with u_file.open("wb") as buf:
        while len(each_chunk := store.stream.read(chunk_size)) > 0:
            buf.write(each_chunk)
    if u_file.stat().st_size == 0:
        flash("File is empty. Please try again.", category="error")
        u_file.unlink()
        return
    flash("File uploaded.", category="success")
    return u_file


def handle_upload():
    """Handle upload."""
    r_file = request.files["file"]
    if not (s_file := _check_file(r_file.filename, r_file.mimetype)):
        return
    if not (u_file := _upload_file(s_file, r_file)):
        return
    action.delay(str(u_file.absolute()), s_file)
    u_file.unlink()  # comment to verify


def handle_query(query_text):
    """Handle Query."""
    with db.engine.connect() as conn:
        result = conn.execute(text(query_text))
        rc = result.rowcount
    # SELECT * FROM user;
    # SELECT * FROM product_data WHERE price > 20;
    flash(f"{rc} record{'' if rc == 1 else 's'} found.", category="info")
