import duckdb
import pandas as pd
from datalakesurfer.query.base_query import ADLSBaseQueryRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential
from fsspec import filesystem

class ADLSIcebergQueryRetriever(ADLSBaseQueryRetriever):
    """
    Query Iceberg tables in ADLS Gen2 using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:

        try:
            credential = CustomTokenCredential(
                token=self.token,
                expires_on=self.expires_on
            )
            fs = filesystem("abfs", account_name=self.account_name, credential=credential)
            conn = duckdb.connect()
            conn.register_filesystem(fs)
            conn.sql("INSTALL iceberg; LOAD iceberg;")
            # Register Iceberg tables
            for alias, iceberg_path in tables.items():
                full_path = f"abfs://{self.file_system_name}@{self.account_name}.dfs.core.windows.net/{iceberg_path}"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM iceberg_scan('{full_path}', allow_moved_paths=true)")
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.unregister_filesystem("abfs")
            conn.close()