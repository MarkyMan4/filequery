import unittest
import os
import sys

# add src folder to path so filequery can be imported
src_path = os.path.join(os.getcwd(), 'src')
sys.path.append(src_path)

# add sample data dir to path
sample_data_path = os.path.join(os.getcwd(), 'example')
sys.path.append(sample_data_path)

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

if __name__ == '__main__':
    unittest.main()
    
    # for one-off testing
    # fdb = FileDb('example/test.csv')
    # res = fdb.exec_query('select * from test')
    
    # print(res)
