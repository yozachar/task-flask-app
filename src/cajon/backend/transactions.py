"""Transactions."""

# standard
from os import environ
from pathlib import Path

# external
from dask.dataframe import read_csv  # pyright: ignore[reportPrivateImportUsage]
from dotenv import load_dotenv

# local
# from . import cajon

load_dotenv()


def csv_to_sql(source: Path):
    """CSV to SQL."""
    # TODO: optimize
    _pg_user = environ["POSTGRES_USER"]
    _pg_passwd = environ["POSTGRES_PASSWORD"]
    _db_host = environ["PG_DB_HOST"]
    _db_port = environ["PG_DB_PORT"]
    _db_name = environ["POSTGRES_DB"]
    uri = f"postgresql+psycopg://{_pg_user}:{_pg_passwd}@{_db_host}:{_db_port}/{_db_name}"

    t_name = source.name.split(" ")[0]
    ddf = read_csv(source)
    ddf.to_sql(t_name, uri, if_exists="replace", method="multi")


# ----> use for testing <----
# def action():
#     """Action."""
#     source = cajon / "backend/uploads/product_data 2024-07-23 16:30:01.590859.csv"
#     csv_to_sql(source)
