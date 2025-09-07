import os
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import S3BaseQueryRetriever

class S3DeltaQueryRetriever(S3BaseQueryRetriever):
    """
    Query Delta tables in S3 using DuckDB SQL with pushdown capability.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            # Create S3 secret for DuckDB session
            conn.sql(f"""
                CREATE OR REPLACE SECRET s3_secret (
                    TYPE s3,
                    PROVIDER config,
                    KEY_ID '{self.aws_access_key_id}',
                    SECRET '{self.aws_secret_access_key}',
                    REGION '{self.aws_region}'
                );
            """)
            conn.sql("INSTALL delta; LOAD delta;")
            # Register Delta tables using delta_scan
            for alias, delta_path in tables.items():
                full_path = f"s3://{delta_path}"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM delta_scan('{full_path}')")
            # Run the query with pushdown
            return conn.execute(query).df()
        finally:
            conn.close()