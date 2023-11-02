import os
from typing import List

import duckdb

from .exceptions import InvalidFileTypeException
from .filetype import FileType
from .queryresult import QueryResult

READ_FUNCS = {
    FileType.CSV: "read_csv_auto",
    FileType.PARQUET: "read_parquet",
    FileType.JSON: "read_json_auto",
    FileType.NDJSON: "read_ndjson_auto",
}

# mapping from file extension to FileType
FILE_EXT_MAP = {
    "csv": FileType.CSV,
    "parquet": FileType.PARQUET,
    "json": FileType.JSON,
    "ndjson": FileType.NDJSON,
}


class FileDb:
    def __init__(self, filepath: str):
        """
        FileDb constructor

        :param filepath: path to a file or directory containing files which will be read into tables
        :type filepath: str
        """
        self.db = duckdb.connect(":memory:")

        # filename should be path to file
        def create_table_from_file(filename: str):
            base_filename = os.path.basename(filename).lower()
            file_ext = base_filename.split(".")[-1]
            filetype = FILE_EXT_MAP.get(file_ext)

            if filetype is None:
                raise InvalidFileTypeException

            table_name = os.path.splitext(base_filename)[0]
            read_func = READ_FUNCS[filetype]

            self.db.execute(
                f"create table {table_name} as select * from {read_func}('{filename}');"
            )

        if os.path.isdir(filepath):
            # only take accepted file types
            files = []
            for file in os.listdir(filepath):
                is_accepted_type = (
                    file.lower().endswith(".csv")
                    or file.lower().endswith(".parquet")
                    or file.lower().endswith(".json")
                    or file.lower().endswith(".ndjson")
                )

                if is_accepted_type:
                    files.append(file)

            for file in files:
                create_table_from_file(os.path.join(filepath, file))
        else:
            create_table_from_file(filepath)

    def exec_query(self, query: str) -> QueryResult:
        """
        Executes a query in the database created from the file. If more than one semicolon separated queries are given,
        the result will only be given for the last one. Use the exec_many_queries() to get the result from multiple queries.

        :param query: query to execute
        :type query: str
        :return: result of executing the query
        :rtype: QueryResult
        """
        res = self.db.execute(query)
        return QueryResult(res.fetchnumpy())

    def exec_many_queries(self, queries: List[str]) -> List[QueryResult]:
        results = [self.exec_query(query) for query in queries]
        return results

    def export_query(
        self, query: str, output_filepath: str, filetype: int = FileType.CSV, **kwargs
    ):
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
            delimiter = "," if "delimiter" not in kwargs else kwargs["delimiter"]
            self.db.execute(
                f"copy ({query}) to '{output_filepath}' (header, delimiter '{delimiter}')"
            )
        elif filetype == FileType.PARQUET:
            self.db.execute(f"copy ({query}) to '{output_filepath}'")
