import json
import os
import tempfile
import gcsfs
import pyarrow.dataset as ds
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import GCSBaseQueryRetriever

class GCSParquetQueryRetriever(GCSBaseQueryRetriever):
    """
    Query multiple Parquet datasets in GCS using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            fs = gcsfs.GCSFileSystem(token=self.service_account_info)
            # Register Parquet tables
            for alias, parquet_path in tables.items():
                dataset = ds.dataset(parquet_path, filesystem=fs, format="parquet", partitioning="hive")
                conn.register(alias, dataset.to_table())
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.close()