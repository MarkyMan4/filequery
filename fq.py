import argparse
import sys
from filequery import filedb
from dataclasses import dataclass

@dataclass
class FileQueryArgs:
    filename: str
    query: str
    query_file: str
    out_file: str

def parse_arguments() -> FileQueryArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', required=True, help='path to CSV or Parquet file')
    parser.add_argument('--query', required=False, help='SQL query to execute against file')
    parser.add_argument('--query_file', required=False, help='path to file with query to execute')
    parser.add_argument('--out_file', required=False, help='file to write results to instead of printing to standard output')
    args = parser.parse_args()

    return FileQueryArgs(
        args.filename, 
        args.query, 
        args.query_file,
        args.out_file
    )

def main():
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

    filetype = filedb.FileType.CSV if args.filename.endswith('.csv') else filedb.FileType.PARQUET

    try:
        fdb = filedb.FileDb(args.filename, filetype)
        query_result = fdb.exec_query(query)

        if args.out_file:
            query_result.save_to_file(args.out_file)
        else:
            print(str(query_result))
    except Exception as e:
        print('failed to query file')
        print(e)
        sys.exit()

if __name__ == '__main__':
    main()
