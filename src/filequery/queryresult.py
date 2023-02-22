import numpy as np
from typing import List, Dict, Any

class QueryResult:
    result_cols: List[str]
    records: List[List[Any]]

    def __init__(self, result: Dict[str, np.ndarray]):
        self.result_cols = list(result.keys())
        recs_as_cols = [result[col] for col in result]
        self.records = np.transpose(recs_as_cols).tolist()

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
        """
        Saves query reslt as a CSV

        :param filepath: path to output file
        :type filepath: str
        """
        with open(filepath, 'w') as outfile:
            outfile.write(str(self))
