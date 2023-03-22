import numpy as np
from tabulate import tabulate
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
        # formats as a csv
        return self.format_with_delimiter(',')
    
    def format_with_delimiter(self, delimiter):
        header_str = delimiter.join(map(self.__format_field, self.result_cols))
        records_str = '\n'.join([delimiter.join(map(self.__format_field, rec)) for rec in self.records])

        return f'{header_str}\n{records_str}'

    def format_as_table(self, delimiter: str = None) -> str:
        """
        Formats query result as a string in a tabular format

        :param delimiter: specify a delimiter to format like a delimited file, if not specified, the result will be a "pretty" format, defaults to None
        :type delimiter: str, optional
        :return: query result as a tabular-formatted string
        :rtype: str
        """
        if delimiter:
            return self.format_with_delimiter(delimiter)

        return tabulate(self.records, headers=self.result_cols, tablefmt='fancy_grid')

    def save_to_file(self, filepath: str, delimiter: str = ','):
        """
        Saves query reslt as a CSV

        :param filepath: path to output file
        :type filepath: str
        :param delimiter: delimiter to use in output file, defaults to ','
        :type filepath: str
        """
        with open(filepath, 'w') as outfile:
            outfile.write(self.format_with_delimiter(delimiter))
