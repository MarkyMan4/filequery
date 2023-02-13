import argparse
import sys
from database import file_db
from dataclasses import dataclass

@dataclass
class FileQueryArgs:
    filename: str
    query: str
    query_file: str

def parse_arguments() -> FileQueryArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', required=True, help='path to CSV or Parquet file')
    parser.add_argument('--query', required=False, help='SQL query to execute against file')
    parser.add_argument('--query_file', required=False, help='path to file with query to execute')
    args = parser.parse_args()

    return FileQueryArgs(
        args.filename, 
        args.query, 
        args.query_file
    )

def format_field(field):
    formatted = field

    if type(field) == str:
        formatted = f'"{field}"'
    elif field == None:
        formatted = ''
    else:
        formatted = str(field)

    return formatted

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

    filetype = file_db.FileType.CSV if args.filename.endswith('.csv') else file_db.FileType.PARQUET

    try:
        fdb = file_db.FileDb(args.filename, filetype)
        records, result_cols = fdb.exec_query(query)

        # format as csv for output
        print(','.join(map(format_field, result_cols)))
        print('\n'.join([','.join(map(format_field, rec)) for rec in records]))
    except Exception as e:
        print('failed to query file')
        print(e)
        sys.exit()

if __name__ == '__main__':
    main()
