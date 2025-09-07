import duckdb
import pandas as pd
from datalakesurfer.query.base_query import FabricBaseQueryRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential
from adlfs import AzureBlobFileSystem

class FabricIcebergQueryRetriever(FabricBaseQueryRetriever):
    """
    Query Iceberg tables in Microsoft Fabric OneLake using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        try:
            credential = CustomTokenCredential(token=self.token, expires_on=self.expires_on)
            fs = AzureBlobFileSystem(account_name="onelake", anon=False, credential=credential)
            fs.account_host = "onelake.blob.fabric.microsoft.com"
            fs.do_connect()
            conn = duckdb.connect()
            conn.register_filesystem(fs)
            conn.sql("INSTALL iceberg; LOAD iceberg;")
            # Register Iceberg tables
            for alias, iceberg_path in tables.items():
                full_path = f"abfs://{self.file_system_name}@{self.account_name}.dfs.fabric.microsoft.com/{iceberg_path}"
                conn.sql(f"CREATE VIEW {alias} AS SELECT * FROM iceberg_scan('{full_path}', allow_moved_paths=true)")
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.unregister_filesystem(name="abfs")
            conn.close()