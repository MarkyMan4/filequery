import argparse
import sys
from filequery.filedb import FileDb, FileType
from dataclasses import dataclass

@dataclass
class FileQueryArgs:
    filename: str
    query: str
    query_file: str
    out_file: str
    out_file_format: str

def parse_arguments() -> FileQueryArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', required=True, help='path to CSV or Parquet file')
    parser.add_argument('--query', required=False, help='SQL query to execute against file')
    parser.add_argument('--query_file', required=False, help='path to file with query to execute')
    parser.add_argument('--out_file', required=False, help='file to write results to instead of printing to standard output')
    parser.add_argument('--out_file_format', required=False, help='either csv or parquet, defaults to csv')
    args = parser.parse_args()

    return FileQueryArgs(
        args.filename, 
        args.query, 
        args.query_file,
        args.out_file,
        args.out_file_format
    )

def fq_cli_handler():
    args = parse_arguments()

    if not args.query and not args.query_file:
        print('you must provide either a query or a path to a file with a query')
        sys.exit()

    query = args.query

    if args.query_file:
        try:
            with open(args.query_file) as f:
                query = ''.join(f.readlines())
        except:
            print('error readin query file')
            sys.exit()

    filetype = FileType.CSV if args.filename.endswith('.csv') else FileType.PARQUET

    try:
        fdb = FileDb(args.filename, filetype)

        if args.out_file:
            outfile_type = FileType.PARQUET if args.out_file_format == 'parquet' else FileType.CSV
            fdb.export_query(query, args.out_file, outfile_type)
        else:
            query_result = fdb.exec_query(query)
            print(str(query_result))
    except Exception as e:
        print('failed to query file')
        print(e)
        sys.exit()
