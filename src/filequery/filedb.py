import os
import re
from typing import List

import duckdb

from .exceptions import InvalidFileTypeException
from .filetype import FileType
from .queryresult import QueryResult

READ_FUNCS = {
    FileType.CSV: "read_csv",
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
                self._create_table_from_file(os.path.join(filepath, file))
        else:
            self._create_table_from_file(filepath)

    def _create_table_from_file(self, filepath: str):
        """
        create a table in the database from a file

        :param filename: path to a CSV, JSON or Parquet file
        :type filename: str
        :raises InvalidFileTypeException: raised if file is not CSV, JSON or Parquet
        """
        base_filename = os.path.basename(filepath).lower()
        table_name, file_ext = os.path.splitext(base_filename)
        file_ext = file_ext.replace(".", "")
        filetype = FILE_EXT_MAP.get(file_ext)

        if filetype is None:
            raise InvalidFileTypeException

        read_func = READ_FUNCS[filetype]

        if self._should_quote_table_name(table_name):
            table_name = f'"{table_name}"'

        # for csv, json and ndjson, set sample size to -1 (sample all records)
        # this is not needed for parquet
        if filetype == FileType.PARQUET:
            self.db.execute(
                f"create table {table_name} as select * from {read_func}('{filepath}');"
            )
        else:
            self.db.execute(
                f"create table {table_name} as select * from {read_func}('{filepath}', SAMPLE_SIZE=-1);"
            )

    def _should_quote_table_name(self, table_name: str) -> bool:
        """
        Determine if a table name needs to be wrapped in double quotes. It needs to be wrapped 
        in quotes if it does not follow these rules:
        - starts with a number or special characters
        - contains whitespace or special characters
        - it is a reserved word

        :param table_name: name of table to check - this is the file name without the extension
        :type table_name: str
        :return: whether the table name needs to be wrapped in double quotes
        :rtype: bool
        """
        # first check if it starts with a number or special character, or if it contains special characters
        valid_table_name_regex = re.compile("^[a-zA-Z_]+[a-zA-Z0-9_]+$")
        if not valid_table_name_regex.match(table_name):
            return True

        # then check if it's a reserved word - using DuckDB's function duckdb_keywords()
        query = f"""
            select *
            from duckdb_keywords()
            where keyword_name = '{table_name.lower()}'
        """

        res = self.db.execute(query)
        if len(res.fetchall()) > 0:
            return True
        
        return False

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
        elif filetype == FileType.JSON:
            self.db.execute(f"copy ({query}) to '{output_filepath}' (ARRAY true)")
        elif filetype == FileType.PARQUET:
            self.db.execute(f"copy ({query}) to '{output_filepath}'")
