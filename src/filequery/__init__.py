import argparse
import json
import sys
from filequery.file_query_args import FileQueryArgs
from filequery.filedb import FileDb, FileType
from typing import List

def parse_arguments(parser: argparse.ArgumentParser) -> FileQueryArgs:
    parser.add_argument('--filename', required=False, help='path to a CSV, Parquet or JSON file')
    parser.add_argument('--filesdir', required=False, help='path to a directory which can contain a combination of CSV, Parquet and JSON files')
    parser.add_argument('--query', required=False, help='SQL query to execute against file')
    parser.add_argument('--query_file', required=False, help='path to file with query to execute')
    parser.add_argument('--out_file', nargs='+', required=False, help='file to write results to instead of printing to standard output')
    parser.add_argument('--out_file_format', required=False, help='either csv or parquet, defaults to csv')
    parser.add_argument('--delimiter', required=False, help='delimiter to use when printing result or writing to CSV file')
    parser.add_argument('--config', required=False, help='path to JSON config file')
    args = parser.parse_args()

    cli_args = None

    # if config file given, all other arguments are ignored
    if args.config:
        try:
            cli_args = parse_config_file(args.config)
        except:
            print('failed to load config file')
            sys.exit()
    else:
        cli_args = FileQueryArgs(
            args.filename, 
            args.filesdir,
            args.query, 
            args.query_file,
            args.out_file,
            args.out_file_format,
            args.delimiter
        )

    return cli_args

def parse_config_file(config_file: str):
    args = None

    with open(config_file) as cf:
        config = json.load(cf)

        # need to convert outfile to list if a single outfile is specified
        outfiles = config.get('out_file')
        if outfiles and type(outfiles) == str:
            outfiles = [config.get('out_file')]

        args = FileQueryArgs(
            config.get('filename'),
            config.get('filesdir'),
            config.get('query'),
            config.get('query_file'),
            outfiles,
            config.get('out_file_format'),
            config.get('delimiter')
        )
    
    return args

def validate_args(args: FileQueryArgs) -> str:
    err_msg = None

    if not args.filename and not args.filesdir:
        err_msg = 'you must provide either a file name or a path to a directory containing CSV and/or Parquet files'

    if args.filename and args.filesdir:
        err_msg = 'you cannot provide both filename and filesdir'

    if not args.query and not args.query_file:
        err_msg = 'you must provide either a query or a path to a file with a query'

    if args.query and args.query_file:
        err_msg = 'you cannot provide both query and query_file'
        
    return err_msg

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
            # print(qr.format_as_table())
            yield qr
    else:
        query_result = fdb.exec_query(queries[0])
        # print(query_result.format_as_table())
        yield query_result

# determines what to do based on arguments provided
# having this separate from fq_cli_handler() makes unit testing easier
def handle_args(args: FileQueryArgs):
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

        queries = split_queries(query)

        if args.out_file:
            if len(args.out_file) != len(queries):
                print('number of queries and output files do not match')
                sys.exit()
            
            outfile_type = FileType.PARQUET if args.out_file_format == 'parquet' else FileType.CSV

            for i in range(len(queries)):
                delimiter = args.delimiter if args.delimiter else ','
                fdb.export_query(queries[i], args.out_file[i], outfile_type, delimiter=delimiter)
        else:
            queries = split_queries(query)
            for query_result in run_sql(fdb, queries):
                print(query_result.format_as_table(args.delimiter))
    except Exception as e:
        print('failed to query file')
        print(e)
        sys.exit()

def fq_cli_handler():
    parser = argparse.ArgumentParser()
    args = parse_arguments(parser)

    err = validate_args(args)

    if(err):
        print(f'{err}\n')
        parser.print_help()
        sys.exit()
        
    handle_args(args)
