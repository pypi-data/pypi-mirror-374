import json
import os
import tempfile
import gcsfs
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import GCSBaseQueryRetriever

class GCSParquetQueryRetriever(GCSBaseQueryRetriever):
    """
    Query multiple Parquet datasets in GCS using DuckDB SQL with pushdown capability.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            fs = gcsfs.GCSFileSystem(token=self.service_account_info)
            conn.register_filesystem(fs)
            # Register Parquet tables using parquet_scan
            for alias, parquet_path in tables.items():
                full_path = f"gs://{parquet_path}/**/*.parquet"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM parquet_scan('{full_path}')")
            # Run the query with pushdown
            return conn.execute(query).df()
        finally:
            conn.close()