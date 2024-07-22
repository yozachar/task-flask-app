"""Main."""

# local
from .backend import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]

# instructions to run commands in separate terminals

# podman-compose -p cajon -f compose up -d
# celery -A src.cajon.main worker --loglevel INFO
# flask -A src.cajon.main run
