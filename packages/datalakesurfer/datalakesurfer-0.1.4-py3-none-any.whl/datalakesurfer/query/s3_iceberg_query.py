import s3fs
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import S3BaseQueryRetriever

class S3IcebergQueryRetriever(S3BaseQueryRetriever):
    """
    Query Iceberg tables in S3 using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            fs = s3fs.S3FileSystem(
                key=self.aws_access_key_id,
                secret=self.aws_secret_access_key
            )
            conn.register_filesystem(fs)
            conn.sql("INSTALL iceberg; LOAD iceberg;")
            # Register Iceberg tables
            for alias, iceberg_path in tables.items():
                full_path = f"s3://{iceberg_path}"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM iceberg_scan('{full_path}', allow_moved_paths=true)")
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.close()