from typing import List, Any

class QueryResult:
    result_cols: List[str]
    records: List[List[Any]]

    def __init__(self, result_cols: List[str], records: List[List[Any]]):
        self.result_cols = result_cols
        self.records = records

    def __format_field(self, field) -> str:
        formatted = field

        if type(field) == str:
            formatted = f'"{field}"'
        elif field == None:
            formatted = ''
        else:
            formatted = str(field)

        return formatted

    def __str__(self) -> str:
        header_str = ','.join(map(self.__format_field, self.result_cols))
        records_str = '\n'.join([','.join(map(self.__format_field, rec)) for rec in self.records])

        return f'{header_str}\n{records_str}'

    def save_to_file(self, filepath: str):
        with open(filepath, 'w') as outfile:
            outfile.write(str(self))
