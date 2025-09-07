import s3fs
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import S3BaseQueryRetriever

class S3ParquetQueryRetriever(S3BaseQueryRetriever):
    """
    Query multiple Parquet datasets in S3 using DuckDB SQL with pushdown capability.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            fs = s3fs.S3FileSystem(
                key=self.aws_access_key_id,
                secret=self.aws_secret_access_key
            )
            conn.register_filesystem(fs)
            # Register Parquet tables using parquet_scan
            for alias, parquet_path in tables.items():
                full_path = f"s3://{parquet_path}/**/*.parquet"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM parquet_scan('{full_path}')")
            # Run the query with pushdown
            return conn.execute(query).df()
        finally:
            conn.close()