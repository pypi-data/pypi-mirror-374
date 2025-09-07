import duckdb
import pandas as pd
import os
from datalakesurfer.query.base_query import ADLSBaseQueryRetriever

class ADLSDeltaQueryRetriever(ADLSBaseQueryRetriever):
    """
    Query multiple Delta tables in Azure Data Lake Storage Gen2 using DuckDB SQL with pushdown capability.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            # Set transport option for Azure (recommended for *nix systems)
            conn.sql("SET azure_transport_option_type = 'curl';")
            conn.sql(f"""
                CREATE SECRET azure_token_secret (
                     TYPE AZURE,
                     PROVIDER access_token,
                     ACCOUNT_NAME '{self.account_name}',
                     ACCESS_TOKEN '{self.token}'
                     );
            """)
            conn.sql("INSTALL delta; LOAD delta;")
            # Register Delta tables using delta_scan
            for alias, delta_path in tables.items():
                full_path = f"abfss://{self.file_system_name}@{self.account_name}.dfs.core.windows.net/{delta_path}"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM delta_scan('{full_path}')")
            # Run the query with pushdown
            result_df = conn.execute(query).df()
            return result_df
        finally:
            conn.close()