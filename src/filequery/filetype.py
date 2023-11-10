from enum import Enum


class FileType(Enum):
    CSV = 0
    PARQUET = 1
    JSON = 2
    NDJSON = 3
