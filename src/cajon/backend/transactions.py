"""Transactions."""

# standard
from logging import DEBUG, log
from pathlib import Path

# external
from dask.dataframe import read_csv  # pyright: ignore[reportPrivateImportUsage]
import psycopg
from psycopg.rows import TupleRow

# local
from . import cajon, get_pg_uri

_dtype_to_pgtype = {
    "bool": "boolean",
    "int8": "smallint",
    "int16": "smallint",
    "int32": "integer",
    "int64": "bigint",
    "float32": "real",
    "float64": "double precision",
    "object": "text",
    "datetime64[ns]": "timestamp",
    "timedelta[ns]": "interval",
    "string": "text",
    "category": "text",
}


def _get_pgtype(dtype):
    dtype_str = str(dtype)
    return _dtype_to_pgtype.get(dtype_str) or "text"


def _complete_transaction(conn: psycopg.Connection[TupleRow], commit: bool = False):
    if commit:
        conn.commit()
    conn.close()


def _read_csv_headers(source: Path):
    ddf = read_csv(source)
    field_n_types = ""
    for col in ddf.columns:
        col_name, col_type = col, _get_pgtype(ddf[col].dtype)
        col_name = col_name.replace(":", "").replace(".", "_").replace(" ", "_")
        field_n_types += f"{col_name} {col_type}, "
    field_n_types = field_n_types[:-2]
    return field_n_types


def _copy_csv2sql(cur: psycopg.Cursor[TupleRow], source: Path):
    create_table_sql = f"CREATE TABLE IF NOT EXISTS companies_sorted ({_read_csv_headers(source)})"
    cur.execute(create_table_sql)  # pyright: ignore[reportArgumentType]
    with cur.copy("COPY companies_sorted FROM STDIN WITH (FORMAT CSV)") as copy:
        with source.open() as csv_f:
            next(csv_f)
            while data := csv_f.read(50):
                copy.write(data)


def csv_to_sql(source: Path):
    """Copy CSV to PostgresSQL."""
    with psycopg.connect(get_pg_uri()) as conn:
        with conn.cursor() as cur:
            result = cur.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_tables "
                + "WHERE schemaname = 'public' AND tablename = 'companies_sorted');"
            )
            if (exists := result.fetchone()) and exists[0]:
                return _complete_transaction(conn)
            _copy_csv2sql(cur, source)
        _complete_transaction(conn, commit=True)


# ----> TODO: use for testing <----
def action():
    """Action."""
    source = cajon / "backend/uploads/product_data 2024-07-23 16:43:55.708747.csv"
    # source = cajon / "backend/uploads/companies_sorted.csv"
    try:
        csv_to_sql(source)
    except psycopg.Error as e:
        log(DEBUG, e)  # TODO: remove in production
