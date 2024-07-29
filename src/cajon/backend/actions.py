"""Upload task."""

# standard
from asyncio import get_event_loop
from datetime import datetime
from pathlib import Path

# external
import aiofiles
from flask import flash, request
from sqlalchemy import text
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# local
from . import cajon, db
from .transactions import action

ev_loop = get_event_loop()
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
        return
    return secure_filename(name).split(".", -1)[0] + " " + str(datetime.now()) + ".csv"


async def _upload_file(u_file: Path, store: FileStorage):
    flash("Uploading file ...", category="info")
    chunk_size = 1024**2  # 1MB
    async with aiofiles.open(u_file, "wb") as buf:
        while len(each_chunk := store.stream.read(chunk_size)) > 0:
            await buf.write(each_chunk)
    if u_file.stat().st_size == 0:
        flash("File is empty. Please try again.", category="error")
        u_file.unlink()
        return
    flash("File uploaded.", category="success")


def handle_upload():
    """Handle upload."""
    r_file = request.files["file"]
    if not (s_file := _check_file(r_file.filename, r_file.mimetype)):
        flash("Invalid file or filename.", category="error")
        return
    u_file = UPLOAD_FOLDER / s_file
    try:
        ev_loop.run_until_complete(_upload_file(u_file, r_file))
    except Exception:
        flash("Error uploading file.", category="error")
        return
    action.delay(str(u_file.absolute()), s_file)


def handle_query(query_text: str):
    """Handle Query."""
    rc = 0
    with db.engine.connect() as conn:
        result = conn.execute(text(query_text))
        rc = result.rowcount
    # SELECT * FROM user;
    # SELECT * FROM product_data WHERE price > 20;
    flash(f"{rc} record{'' if rc == 1 else 's'} found.", category="info")
