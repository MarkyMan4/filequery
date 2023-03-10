from dataclasses import dataclass

@dataclass
class FileQueryArgs:
    filename: str
    filesdir: str
    query: str
    query_file: str
    out_file: str
    out_file_format: str
