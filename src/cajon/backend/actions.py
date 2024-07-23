"""Upload task."""

# standard
from datetime import datetime

# external
from celery import shared_task
from flask import flash, request
from sqlalchemy import text
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# local
from . import cajon, db
from .transactions import action, csv_to_sql

ALLOWED_EXTENSIONS = ("CSV",)
UPLOAD_PATH = cajon / "backend/uploads"
if not UPLOAD_PATH.exists():
    UPLOAD_PATH.mkdir(parents=True)


@shared_task
def handle_upload():
    """Handle upload."""
    # filename = r_file.filename

    # if not filename or (
    #     "." not in filename
    #     or len(filename) < 3
    #     or filename.rsplit(".", 1)[1].upper() not in ALLOWED_EXTENSIONS
    # ):
    #     flash("Invalid file or filename.", category="error")
    #     return

    # s_file = secure_filename(filename).split(".", -1)[0] + " " + str(datetime.now()) + ".csv"
    # # r_file.save(UPLOAD_PATH / s_file)
    # chunk_size = 4096
    # uploaded_file = UPLOAD_PATH / s_file
    # with uploaded_file.open("wb") as buf:
    #     while len(each_chunk := request.stream.read(chunk_size)) > 0:
    #         buf.write(each_chunk)

    # if uploaded_file.stat().st_size == 0:
    #     flash("File is empty. Please try again.", category="error")
    #     uploaded_file.unlink()
    #     return

    # csv_to_sql(uploaded_file)
    action()
    flash("File uploaded successfully.", category="success")
    # uploaded_file.unlink()


def handle_query(query_text):
    """Handle Query."""
    with db.engine.connect() as conn:
        result = conn.execute(text(query_text))
        rc = result.rowcount
    # SELECT * FROM user;
    # SELECT * FROM product_data WHERE price > 20;
    flash(f"{rc} record{'' if rc == 1 else 's'} found.", category="info")
