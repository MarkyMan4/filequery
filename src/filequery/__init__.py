import argparse
import sys
from dataclasses import dataclass
from filequery.filedb import FileDb, FileType
from typing import List

@dataclass
class FileQueryArgs:
    filename: str
    filesdir: str
    query: str
    query_file: str
    out_file: str
    out_file_format: str

def parse_arguments() -> FileQueryArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', required=False, help='path to CSV or Parquet file')
    parser.add_argument('--filesdir', required=False, help='path to a directory which can contain a combination of CSV and Parquet files')
    parser.add_argument('--query', required=False, help='SQL query to execute against file')
    parser.add_argument('--query_file', required=False, help='path to file with query to execute')
    parser.add_argument('--out_file', required=False, help='file to write results to instead of printing to standard output')
    parser.add_argument('--out_file_format', required=False, help='either csv or parquet, defaults to csv')
    args = parser.parse_args()

    if not args.filename and not args.filesdir:
        print('you must provide either a file name or a path to a directory containing CSV and/or Parquet files\n')
        parser.print_help()
        sys.exit()

    if args.filename and args.filesdir:
        print('you cannot provide both filename and filesdir\n')
        parser.print_help()
        sys.exit()

    if not args.query and not args.query_file:
        print('you must provide either a query or a path to a file with a query\n')
        parser.print_help()
        sys.exit()

    if args.filename and args.filesdir:
        print('you cannot provide both query and query_file\n')
        parser.print_help()
        sys.exit()

    return FileQueryArgs(
        args.filename, 
        args.filesdir,
        args.query, 
        args.query_file,
        args.out_file,
        args.out_file_format
    )

def split_queries(sql: str) -> List[str]:
    """
    Split semicolon separated SQL to a list

    :param sql: SQL to split
    :type sql: str
    :return: List of SQL statements
    :rtype: List[str]
    """
    queries = sql.split(';')

    if queries[-1].strip() in ('', '\n', '\r', '\t'):
        queries = queries[:-1]

    return queries

def run_sql(fdb: FileDb, queries: List[str]):
    if len(queries) > 1:
        query_results = fdb.exec_many_queries(queries)
        for qr in query_results:
            print(qr.format_as_table())
    else:
        query_result = fdb.exec_query(queries[0])
        print(query_result.format_as_table())

def fq_cli_handler():
    args = parse_arguments()

    query = args.query

    if args.query_file:
        try:
            with open(args.query_file) as f:
                query = ''.join(f.readlines())
        except:
            print('error reading query file')
            sys.exit()

    try:
        filepath = args.filename if args.filename else args.filesdir
        fdb = FileDb(filepath)

        if args.out_file:
            outfile_type = FileType.PARQUET if args.out_file_format == 'parquet' else FileType.CSV
            fdb.export_query(query, args.out_file, outfile_type)
        else:
            queries = split_queries(query)
            print(queries)
            run_sql(fdb, queries)
    except Exception as e:
        print('failed to query file')
        print(e)
        sys.exit()
