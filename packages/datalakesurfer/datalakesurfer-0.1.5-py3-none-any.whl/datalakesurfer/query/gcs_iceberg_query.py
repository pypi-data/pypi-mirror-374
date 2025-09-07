import gcsfs
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import GCSBaseQueryRetriever

class GCSIcebergQueryRetriever(GCSBaseQueryRetriever):
    """
    Query Iceberg tables in GCS using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            fs = gcsfs.GCSFileSystem(token=self.service_account_info)
            conn.register_filesystem(fs)
            conn.sql("INSTALL iceberg; LOAD iceberg;")
            # Register Iceberg tables
            for alias, iceberg_path in tables.items():
                full_path = f"gs://{iceberg_path}"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM iceberg_scan('{full_path}', allow_moved_paths=true)")
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.close()