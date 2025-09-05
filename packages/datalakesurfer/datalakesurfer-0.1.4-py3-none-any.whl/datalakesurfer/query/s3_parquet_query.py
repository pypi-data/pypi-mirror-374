import s3fs
import pyarrow.dataset as ds
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import S3BaseQueryRetriever

class S3ParquetQueryRetriever(S3BaseQueryRetriever):
    """
    Query multiple Parquet datasets in S3 using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            fs = s3fs.S3FileSystem(
                key=self.aws_access_key_id,
                secret=self.aws_secret_access_key
            )
            # Register Parquet tables
            for alias, parquet_path in tables.items():
                dataset = ds.dataset(parquet_path, filesystem=fs, format="parquet", partitioning="hive")
                conn.register(alias, dataset.to_table())
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.close()