"""Upload task."""

# standard
from datetime import datetime
from pathlib import Path

# external
from celery import shared_task
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = ("CSV",)
UPLOAD_PATH = Path(__file__).parent / "uploads"


@shared_task
def handle_upload(r_file):
    """Handle upload."""
    filename = r_file.filename
    if not filename:
        return False
    if (
        "." in filename
        and len(filename) < 3
        and filename.rsplit(".", 1)[1].upper() not in ALLOWED_EXTENSIONS
    ):
        return False
    s_file = secure_filename(filename).split(".", -1)[0] + " " + str(datetime.now()) + ".csv"
    r_file.save(UPLOAD_PATH / s_file)
    return True
