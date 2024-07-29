"""Transactions."""

# standard
from logging import DEBUG, log
from pathlib import Path
from re import sub

# external
from celery import shared_task
from dask.dataframe import read_csv  # pyright: ignore[reportPrivateImportUsage]
import psycopg
from psycopg.rows import TupleRow

# local
from . import get_pg_uri

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


def _convert_to_valid_table_name(filename: str):
    filename = filename.replace(" ", "_")
    filename = sub(r"^[^a-zA-Z_]+", "", filename)
    filename = sub(r"[^a-zA-Z0-9_$]+", "", filename)
    filename = filename.lower()
    filename = filename[:10]  # 63 is supported, 10 to ease
    return filename


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


def _copy_csv2sql(cur: psycopg.Cursor[TupleRow], source: Path, t_name: str):
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {t_name} ({_read_csv_headers(source)})"
    cur.execute(create_table_sql)  # pyright: ignore[reportArgumentType]
    from_csv_to_sql = f"COPY {t_name} FROM STDIN WITH (FORMAT CSV)"
    with cur.copy(from_csv_to_sql) as copy:  # pyright: ignore[reportArgumentType]
        with source.open("rb") as csv_f:
            next(csv_f)
            while data := csv_f.read(50):
                copy.write(data)


def csv_to_sql(source: Path, t_name: str):
    """Copy CSV to PostgresSQL."""
    with psycopg.connect(get_pg_uri()) as conn:
        with conn.cursor() as cur:
            check_if_table = (
                "SELECT EXISTS (SELECT 1 FROM pg_tables "
                + f"WHERE schemaname = 'public' AND tablename = '{t_name}');"
            )
            result = cur.execute(check_if_table)  # pyright: ignore[reportArgumentType]
            if (exists := result.fetchone()) and exists[0]:
                return _complete_transaction(conn)
            _copy_csv2sql(cur, source, t_name)
        _complete_transaction(conn, commit=True)


@shared_task
def action(source: str, filename: str):
    """Action."""
    # source = cajon / "backend/uploads/product_data 2024-07-23 16:43:55.708747.csv"
    # source = cajon / "backend/uploads/companies_sorted.csv"
    try:
        t_name = _convert_to_valid_table_name(filename)
        # flash("Writing file to Database ...", category="info")
        u_file = Path(source)
        csv_to_sql(u_file, t_name)
        # flash("File written to Database.", category="success")
        u_file.unlink()  # comment to verify
    except psycopg.Error as e:
        log(DEBUG, e)  # TODO: remove in production
