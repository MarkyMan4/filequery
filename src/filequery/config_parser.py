import json
from filequery.file_query_args import FileQueryArgs

class ConfigParser:
    args: FileQueryArgs

    def __init__(self, config_file: str):
        try:
            cf = open(config_file)
            config = json.load(cf)
            self.args = FileQueryArgs(
                config.get('filename'),
                config.get('filesdir'),
                config.get('query'),
                config.get('query_file'),
                config.get('out_file'),
                config.get('out_file_format'),
            )
        except Exception as e:
            print('failed to load config file')
            raise e
