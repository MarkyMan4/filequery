from dataclasses import dataclass
from typing import List


@dataclass
class FileQueryArgs:
    filename: str
    filesdir: str
    query: str
    query_file: str
    out_file: List[str]
    out_file_format: str
    delimiter: str
    editor: bool
