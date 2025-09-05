import adlfs
import pyarrow as pa
import pyarrow.dataset as ds
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import FabricBaseQueryRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential
from adlfs import AzureBlobFileSystem

class FabricParquetQueryRetriever(FabricBaseQueryRetriever):
    """
    Query multiple Parquet datasets in Microsoft Fabric OneLake using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            credential = CustomTokenCredential(token=self.token, expires_on=self.expires_on)
            fs = AzureBlobFileSystem(account_name="onelake", anon=False, credential=credential)
            fs.account_host = "onelake.blob.fabric.microsoft.com"
            fs.do_connect()
            for alias, parquet_path in tables.items():
                full_path = f"{self.file_system_name}/{parquet_path}"
                dataset = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning="hive")
                table = dataset.to_table()
                conn.register(alias, table)
            # Run the query
            return conn.execute(query).df()
        finally:
            conn.close()