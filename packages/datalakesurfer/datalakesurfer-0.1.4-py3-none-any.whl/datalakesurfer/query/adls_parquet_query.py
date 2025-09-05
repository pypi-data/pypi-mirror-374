import adlfs
import pyarrow.dataset as ds
import duckdb
import pandas as pd
from datalakesurfer.query.base_query import ADLSBaseQueryRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential
import pyarrowfs_adlgen2
import pyarrow.fs

class ADLSParquetQueryRetriever(ADLSBaseQueryRetriever):
    """
    Query multiple Parquet datasets in ADLS Gen2 using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            credential = CustomTokenCredential(self.token, self.expires_on)
            handler = pyarrowfs_adlgen2.AccountHandler.from_account_name(
                self.account_name, credential=credential
            )
            fs = pyarrow.fs.PyFileSystem(handler)

            for alias, parquet_path in tables.items():
                full_path = f"{self.file_system_name}/{parquet_path}"
                dataset = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning="hive")
                table = dataset.to_table()
                conn.register(alias, table)
            return conn.execute(query).df()
        finally:
            conn.close()