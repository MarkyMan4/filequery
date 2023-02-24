import duckdb
import os
from .filetype import FileType
from .queryresult import QueryResult

READ_FUNCS = {
    FileType.CSV: 'read_csv_auto',
    FileType.PARQUET: 'read_parquet'
}

class FileDb:
    def __init__(self, filepath: str):
        """
        FileDb constructor

        :param filepath: path to a file or directory containing files which will be read into tables
        :type filepath: str
        """
        self.db = duckdb.connect(':memory:')

        # filename should be path to file
        def create_table_from_file(filename: str):
            base_filename = os.path.basename(filename)
            filetype = FileType.CSV if base_filename.endswith('.csv') else FileType.PARQUET
            table_name = os.path.splitext(base_filename)[0]
            read_func = READ_FUNCS[filetype]

            self.db.execute(f"create table {table_name} as select * from {read_func}('{filename}');")

        if os.path.isdir(filepath):
            # only take csv and parquet files
            files = [file for file in os.listdir(filepath) if file.lower().endswith('.csv') or file.lower().endswith('.parquet')]

            for file in files:
                create_table_from_file(os.path.join(filepath, file))
        else:
            create_table_from_file(filepath)

    def exec_query(self, query: str) -> QueryResult:
        """
        Executes a query in the database created from the file

        :param query: query to execute
        :type query: str
        :return: result of executing the query
        :rtype: QueryResult
        """
        res = self.db.execute(query)
        return QueryResult(res.fetchnumpy())

    def export_query(self, query: str, output_filepath: str, filetype: int = FileType.CSV):
        """
        Writes query result to a file

        :param query: query to execute
        :type query: str
        :param output_filepath: path to output file
        :type output_filepath: str
        :param filetype: output file format (either FileType.CSV or FileType.Parquet), defaults to FileType.CSV
        :type filetype: FileType.CSV
        """
        if filetype == FileType.CSV:
            self.db.execute(f"copy ({query}) to '{output_filepath}' (header, delimiter ',')")
        elif filetype == FileType.PARQUET:
            self.db.execute(f"copy ({query}) to '{output_filepath}'")
