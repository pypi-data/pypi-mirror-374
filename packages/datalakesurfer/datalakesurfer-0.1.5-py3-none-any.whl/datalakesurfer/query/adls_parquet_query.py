import duckdb
import pandas as pd
from datalakesurfer.query.base_query import ADLSBaseQueryRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential
from fsspec import filesystem

class ADLSParquetQueryRetriever(ADLSBaseQueryRetriever):
    """
    Query multiple Parquet datasets in ADLS Gen2 using DuckDB SQL with pushdown capability.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            credential = CustomTokenCredential(
                token=self.token,
                expires_on=self.expires_on
            )
            fs = filesystem("abfs", account_name=self.account_name, credential=credential)
            conn = duckdb.connect()
            conn.register_filesystem(fs)
            # Register Parquet tables using parquet_scan and recursive glob
            for alias, parquet_path in tables.items():
                full_path = f"abfs://{self.file_system_name}@{self.account_name}.dfs.core.windows.net/{parquet_path}/**/*.parquet"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM parquet_scan('{full_path}')")
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.unregister_filesystem("abfs")
            conn.close()
