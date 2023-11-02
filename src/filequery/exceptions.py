class InvalidFileTypeException(Exception):
    """Exception raised for file types that cannot be queried"""

    def __init__(self, file_type):
        super().__init__("file type must be one of: csv, parquet, json, ndjson")
