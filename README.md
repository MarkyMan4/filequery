# filequery
Query CSV and Parquet files using SQL. This uses DuckDB behind the scenes so any valid SQL for DuckDB will work here.

## installation
`$ pip install filequery`

## CLI usage
Run `filequery --help` to see what options are available.

```
usage: __main__.py [-h] [--filename FILENAME] [--filesdir FILESDIR] [--query QUERY] [--query_file QUERY_FILE] [--out_file OUT_FILE] [--out_file_format OUT_FILE_FORMAT] [--config CONFIG]

options:
  -h, --help            show this help message and exit
  --filename FILENAME   path to a CSV, Parquet or JSON file
  --filesdir FILESDIR   path to a directory which can contain a combination of CSV, Parquet and JSON files
  --query QUERY         SQL query to execute against file
  --query_file QUERY_FILE
                        path to file with query to execute
  --out_file OUT_FILE   file to write results to instead of printing to standard output
  --out_file_format OUT_FILE_FORMAT
                        either csv or parquet, defaults to csv
  --config CONFIG       path to JSON config file
```

For basic usage, provide a path to a CSV or Parquet file and a query to execute against it. The table name will be the 
file name without the extension.

`$ filequery --filename example/test.csv --query 'select * from test'`\
`$ filequery --filename example/json_test.json --query 'select nested.nest_id, nested.nested_val from json_test'`\
`$ filequery --filesdir example/data --query 'select * from test inner join test1 on test.col1 = test1.col1'` \
`$ filequery --filesdir example/data --query_file example/queries/join.sql`\
`$ filequery --filesdir example/data --query_file example/queries/json_csv_join.sql`

You can also provide a config file instead of specifying the arguments when running the command.

`$ filequery --config <path to config file>`

The config file should be a json file. See example config file contents below.

```
{
    "filename": "../example/test.csv",
    "query": "select col1, col2 from test"
}
```

```
{
    "filesdir": "../example/data",
    "query_file": "../example/queries/join.sql",
    "out_file": "result.parquet",
    "out_file_format": "parquet"
}
```

## module usage
You can also use filequery in your own programs. See the example below.
```
from filequery.filedb import FileDb

query = 'select * from test'

# read test.csv into a table called "test"
fdb = FileDb('example/test.csv')

# return QueryResult object
res = fdb.exec_query(query)

# formats result as csv
print(str(res))

# saves query result to result.csv
res.save_to_file('result.csv')

# saves query result as parquet file
fdb.export_query(query, 'result.parquet', FileType.PARQUET)
```

## development
Packages required for distribution should go in `requirements.txt`.

To build the wheel:

`$ pip install -r requirements-dev.txt` \
`$ make`

## testing
To test the CLI, cd into the `src` directory and run `filequery` as a module.

`$ python -m filequery <args>`

To run unit tests, stay in the root of the project. The unit tests add `src` to the path so `filequery` can be imported properly.

`$ python tests/<test file>`
