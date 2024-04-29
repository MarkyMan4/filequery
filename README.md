# filequery
[![pypi](https://img.shields.io/pypi/v/filequery.svg)](https://pypi.org/project/filequery/)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarkyMan4/filequery)

Query CSV, JSON and Parquet files using SQL.
- runs queries using a DuckDB in-memory database for efficient querying
- any SQL that works with DuckDB will work here
- use the CLI to easily query files in your terminal or automate queries/transformations as part of a script
- use the TUI for a more interactive experience

## Demo

### CLI

![out](https://github.com/MarkyMan4/filequery/assets/37815834/38b6f69b-297f-4913-826e-89ffbfe483b3)

### TUI

![filequery_tui](https://github.com/MarkyMan4/filequery/assets/37815834/202655ab-359e-4a42-a9eb-49227cf32f22)

![filequery_menu](https://github.com/MarkyMan4/filequery/assets/37815834/57a58e3b-f283-43e9-8a9f-68c363d748af)

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
usage: filequery [-h] [-f FILENAME] [-d FILESDIR] [-q QUERY] [-Q QUERY_FILE] [-o OUT_FILE [OUT_FILE ...]] [-F OUT_FILE_FORMAT] [-D DELIMITER] [-c CONFIG] [-e] [-v]

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
  -v, --version         show program's version number and exit
```

For basic usage, provide a path to a CSV or Parquet file and a query to execute against it. The table name will be the 
file name without the extension. If the file name does not conform to DuckDB's rules for unquoted identifiers, the 
table name will need to be wrapped in double quotes. For example, a file named `my data.csv` would be queried as 
`select * from "my data"`.

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
filequery -e -d path/to/file_directory
```

You can also omit a path to a file or directory and open a blank editor. This can be helpful if 
you want to directly use DuckDB functions such as `read_csv_auto()` for querying your files.

```bash
filequery -e
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
To test the CLI, create a separate virtual environment perform an editable install.

```bash
python -m venv test-env
. test-env/bin/activate
pip install -e .
```

To run unit tests, stay in the root of the project. The unit tests add `src` to the path so `filequery` can be imported properly.

```bash
python tests/test_filequery.py
```
