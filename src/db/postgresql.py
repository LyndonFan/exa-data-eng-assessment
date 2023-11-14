import os
import psycopg2
import polars as pl

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

    def copy_into_table(self, table_name: str, df: pl.DataFrame):
        df.write_database(
            table_name,
            connection=os.environ["PSQL_URI"],
            if_exists="append",
            engine="sqlalchemy",
        )
