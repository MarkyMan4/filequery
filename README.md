# filequery
Query CSV and Parquet files using SQL. This uses DuckDB behind the scenes so any valid SQL for DuckDB will work here.

## Demo

### CLI

![out](https://github.com/MarkyMan4/filequery/assets/37815834/38b6f69b-297f-4913-826e-89ffbfe483b3)

### TUI

![filequery_tui](https://github.com/MarkyMan4/filequery/assets/37815834/56ac5f6f-a8f1-4bcd-9f7f-0721372592d8)

## Installation

```bash
pipx install filequery
```

or

```bash
pip install filequery
```

## CLI usage
Run `filequery --help` to see what options are available.

```
usage: filequery [-h] [-f FILENAME] [-d FILESDIR] [-q QUERY] [-Q QUERY_FILE] [-o OUT_FILE [OUT_FILE ...]] [-F OUT_FILE_FORMAT] [-D DELIMITER] [-c CONFIG] [-e]

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        path to a CSV, Parquet or JSON file
  -d FILESDIR, --filesdir FILESDIR
                        path to a directory which can contain a combination of CSV, Parquet and JSON files
  -q QUERY, --query QUERY
                        SQL query to execute against file
  -Q QUERY_FILE, --query_file QUERY_FILE
                        path to file with query to execute
  -o OUT_FILE [OUT_FILE ...], --out_file OUT_FILE [OUT_FILE ...]
                        file to write results to instead of printing to standard output
  -F OUT_FILE_FORMAT, --out_file_format OUT_FILE_FORMAT
                        either csv or parquet, defaults to csv
  -D DELIMITER, --delimiter DELIMITER
                        delimiter to use when printing result or writing to CSV file
  -c CONFIG, --config CONFIG
                        path to JSON config file
  -e, --editor          run SQL editor UI for exploring data
```

For basic usage, provide a path to a CSV or Parquet file and a query to execute against it. The table name will be the 
file name without the extension.

```bash
filequery --filename example/test.csv --query 'select * from test'
```

## TUI usage

To use the TUI for querying your files, use the `-e` flag and provide a path to a file or directory.

```bash
filequery -e -f path/to/file.csv
```

or

```bash
filequery -e -f path/to/file_directory
```

## Examples

```bash
filequery --filename example/json_test.json --query 'select nested.nest_id, nested.nest_val from json_test' # query json
```
```bash
filequery --filesdir example/data --query 'select * from test inner join test1 on test.col1 = test1.col1' # query multiple files in a directory
```
```bash
filequery --filesdir example/data --query_file example/queries/join.sql # point to a file containing SQL
```
```bash
filequery --filesdir example/data --query_file example/queries/json_csv_join.sql # SQL file joining data from JSON and CSV files
```
```bash
filequery --filesdir example/test.csv --query 'select * from test; select sum(col3) from test;' # output multiple query results to multiple files
```

```bash
filequery --filename example/ndjson_test.ndjson --query 'select id, value, nested.subid, nested.subval from ndjson_test' # query nested JSON in an ndjson file
```

You can also provide a config file instead of specifying the arguments when running the command.

```bash
filequery --config <path to config file>
```

The config file should be a json file. See example config file contents below.

```json
{
    "filename": "../example/test.csv",
    "query": "select col1, col2 from test"
}
```

```json
{
    "filesdir": "../example/data",
    "query_file": "../example/queries/join.sql",
    "out_file": "result.parquet",
    "out_file_format": "parquet"
}
```

See the `example` directory in the repo for more examples.

## Module usage
You can also use filequery in your own programs. See the example below.

```python
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

## Development
Packages required for distribution should go in `requirements.txt`.

To build the wheel:

```bash
pip install -r requirements-dev.txt
make
```

## Testing
To test the CLI, create a separate virtual environment perform an editable.

```bash
python -m venv test-env
. test-env/bin/activate
pip install -e .
```

To run unit tests, stay in the root of the project. The unit tests add `src` to the path so `filequery` can be imported properly.

```bash
python tests/test_filequery.py
```
