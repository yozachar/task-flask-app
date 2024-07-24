FROM docker.io/python:3-slim

ENV SECRET_KEY \
    # postgres
    PG_DB_HOST \
    PG_DB_PORT \
    POSTGRES_USER \
    POSTGRES_DB \
    POSTGRES_PASSWORD
# NOTE: fix unsafe way of handling secrets!

ENV PATH="${PATH}:/root/.local/bin" \
    # python
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100

COPY --chown=root:root . /app/

RUN python -m pip install --root-user-action ignore --upgrade pip \
    && pip install --root-user-action ignore -r /app/requirements.package.txt

WORKDIR /app

CMD flask -A src.cajon.main run & celery -A src.cajon.main worker
# NOTE: do not use this in production!

