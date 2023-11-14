import os
import json
import psycopg2
import polars as pl
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.types import JSON
from dotenv import load_dotenv

load_dotenv()


class PostgreSQL:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.host = os.environ["PSQL_HOST"]
        self.port = os.environ["PSQL_PORT"]
        self.user = os.environ["PSQL_USER"]
        self.password = os.environ["PSQL_PASSWORD"]
        self.database = os.environ["PSQL_DATABASE"]
        self.ssl_mode = "verify-full"
        self.sslrootcert = os.environ["PSQL_SSL_ROOT_CERT"]
        self._connection = None

    def connect(self):
        try:
            self._connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.database,
                sslmode=self.ssl_mode,
                sslrootcert=self.sslrootcert,
            )
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            print("Trying sslmode=require...")
            self._connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.database,
                sslmode="require",
            )
        return

    def connection(self):
        if self._connection is None:
            self.connect()
        return self._connection

    def disconnect(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute_query(self, query, fetch: bool = False):
        res = None
        if not self._connection:
            self.connect()
        with self._connection.cursor() as cursor:
            cursor.execute(query)
            if fetch:
                res = list(cursor.fetchall())
            self._connection.commit()
        return res

    def copy_into_table(
        self,
        table_name: str,
        df: pl.DataFrame,
        json_columns: Optional[list[str]] = None,
    ):
        if json_columns is None:
            json_columns = []
        if not json_columns:
            df.write_database(
                table_name,
                connection=os.environ["PSQL_URI"],
                if_exists="append",
                engine="sqlalchemy",
            )
            return
        pd_df = df.to_pandas()
        engine = create_engine(os.environ["PSQL_URI"])
        for col in json_columns:
            pd_df[col] = pd_df[col].fillna("").map(json.loads)
        pd_df.to_sql(
            table_name,
            con=engine,
            if_exists="append",
            index=False,
            dtype={col: JSON for col in json_columns},
        )
