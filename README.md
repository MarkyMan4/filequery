# filequery
Query CSV and Parquet files using SQL

## installation
`$ pip install filequery`

## CLI usage
Run `filequery --help` to see what options are available.

```
usage: filequery [-h] --filename FILENAME [--query QUERY] [--query_file QUERY_FILE] [--out_file OUT_FILE]

options:
  -h, --help            show this help message and exit
  --filename FILENAME   path to CSV or Parquet file
  --query QUERY         SQL query to execute against file
  --query_file QUERY_FILE
                        path to file with query to execute
  --out_file OUT_FILE   file to write results to instead of printing to standard output
```

For basic usage, provide a path to a CSV or Parquet file and a query to execute against it. The table name will be the 
file name without the extension.

`$ filequery --filename sample_data/test.csv --query 'select * from test'`

## library usage
You can also use filequery in your own programs. See the example below.
```
from filequery.filedb import FileDb

# read test.csv into a table called "test"
db = FileDb('sample_data/test.csv')

# return QueryResult object
res = db.exec_query('select * from test')

# formats result as csv
print(str(res))

# saves query result to result.csv
res.save_to_file('result.csv')
```

## development
Packages required for distribution should go in `requirements.txt`.

To build the wheel:
`$ pip install -r requirements-dev.txt` \
`$ python -m build`

## testing
`$ pip install .` \
`$ python tests/<test file>`
