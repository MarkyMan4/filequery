import unittest
import os
import sys

# add src folder to path so filequery can be imported
src_path = os.path.join(os.getcwd(), 'src')
sys.path.append(src_path)

# add sample data dir to path
sample_data_path = os.path.join(os.getcwd(), 'example')
sys.path.append(sample_data_path)

from filequery import validate_args
from filequery.file_query_args import FileQueryArgs
from filequery.filedb import FileDb
from filequery.queryresult import QueryResult

class TestFileQuery(unittest.TestCase):
    def check_select_star_from_test(self, res: QueryResult):
        self.assertEqual(len(res.records), 3)

        for rec in res.records:
            self.assertEqual(len(rec), 3)

    def test_exec_query(self):
        fdb = FileDb('example/test.csv')
        res = fdb.exec_query('select * from test')
        
        self.check_select_star_from_test(res)

    def test_filesdir_no_trailing_slash(self):
        fdb = FileDb('example/data')
        res = fdb.exec_query('select * from test')
        
        self.check_select_star_from_test(res)

    def test_filesdir_trailing_slash(self):
        fdb = FileDb('example/data/')
        res = fdb.exec_query('select * from test')
        
        self.check_select_star_from_test(res)

    def test_multi_query(self):
        fdb = FileDb('example/data/')
        res = fdb.exec_many_queries([
            'select * from test;',
            'select * from test1;',
            """
            select *
                from test t1
                inner join test1 t2
                on t1.col1 = t2.col1;
            """
        ])

        self.assertEqual(len(res), 3)

class TestFileQueryCli(unittest.TestCase):
    def test_no_filename_or_filesdir(self):
        args = FileQueryArgs(
            filename=None,
            filesdir=None,
            query='select * from test',
            query_file=None,
            out_file=None,
            out_file_format=None
        )

        err = validate_args(args)

        self.assertIsNotNone(err)

    def test_provide_filename_and_filesdir(self):
        args = FileQueryArgs(
            filename='example/test.csv',
            filesdir='example/data',
            query='select * from test',
            query_file=None,
            out_file=None,
            out_file_format=None
        )

        err = validate_args(args)

        self.assertIsNotNone(err)

    def test_no_query_or_query_file(self):
        args = FileQueryArgs(
            filename='example/test.csv',
            filesdir=None,
            query=None,
            query_file=None,
            out_file=None,
            out_file_format=None
        )

        err = validate_args(args)

        self.assertIsNotNone(err)

    def test_provide_query_and_query_file(self):
        args = FileQueryArgs(
            filename='example/test.csv',
            filesdir=None,
            query='select * from test',
            query_file='example/queries/join.sql',
            out_file=None,
            out_file_format=None
        )

        err = validate_args(args)

        self.assertIsNotNone(err)


if __name__ == '__main__':
    unittest.main()
    
    # for one-off testing
    # fdb = FileDb('example/test.csv')
    # res = fdb.exec_query('select * from test')
    
    # print(res)
