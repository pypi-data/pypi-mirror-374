import adlfs
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import FabricBaseQueryRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential

class FabricParquetQueryRetriever(FabricBaseQueryRetriever):
    """
    Query multiple Parquet datasets in Microsoft Fabric Lakehouse using DuckDB SQL with pushdown capability.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            # Create ADLS Gen2 filesystem and register with DuckDB
            credential = CustomTokenCredential(token=self.token, expires_on=self.expires_on)
            fs = adlfs.AzureBlobFileSystem(account_name="onelake", anon=False, credential=credential)
            fs.account_host = "onelake.blob.fabric.microsoft.com"
            fs.do_connect()
            conn = duckdb.connect()
            conn.register_filesystem(fs)
            # Register Parquet tables using parquet_scan and recursive glob
            for alias, parquet_path in tables.items():
                full_path = f"abfs://{self.file_system_name}@{self.account_name}.dfs.fabric.microsoft.com/{parquet_path}/**/*.parquet"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM parquet_scan('{full_path}')")
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.unregister_filesystem("abfs")
            conn.close()
