import duckdb
import os
from .filetype import FileType
from .queryresult import QueryResult

READ_FUNCS = {
    FileType.CSV: 'read_csv_auto',
    FileType.PARQUET: 'read_parquet'
}

class FileDb:
    def __init__(self, filename: str, filetype: int = FileType.CSV):
        self.db = duckdb.connect(':memory:')

        base_filename = os.path.basename(filename)
        table_name = os.path.splitext(base_filename)[0]
        
        read_func = READ_FUNCS[filetype]
        self.db.execute(f"create table {table_name} as select * from {read_func}('{filename}');")

    def exec_query(self, query: str) -> QueryResult:
        res = self.db.execute(query)
        records = res.fetchall()
        result_cols = list(res.fetchnumpy().keys())

        return QueryResult(result_cols, records)
