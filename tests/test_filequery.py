import unittest
import os
import sys

# add src folder to path so filequery can be imported
src_path = os.path.join(os.getcwd(), 'src')
sys.path.append(src_path)

# add sample data dir to path
sample_data_path = os.path.join(os.getcwd(), 'sample_data')
sys.path.append(sample_data_path)

from filequery.filedb import FileDb

class TestFileQuery(unittest.TestCase):
    def test_exec_query(self):
        fdb = FileDb('sample_data/test.csv')
        res = fdb.exec_query('select * from test')
        
        self.assertEqual(len(res.records), 3)

        for rec in res.records:
            self.assertEqual(len(rec), 3)

if __name__ == '__main__':
    unittest.main()
    
    # for one-off testing
    # fdb = FileDb('sample_data/test.csv')
    # res = fdb.exec_query('select * from test')
    
    # print(res)
