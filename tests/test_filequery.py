import os
import sys
import unittest

# add src folder to path so filequery can be imported
src_path = os.path.join(os.getcwd(), "src")
sys.path.append(src_path)

# add sample data dir to path
sample_data_path = os.path.join(os.getcwd(), "example")
sys.path.append(sample_data_path)

from filequery import handle_args, validate_args
from filequery.file_query_args import FileQueryArgs
from filequery.filedb import FileDb, FileType
from filequery.queryresult import QueryResult


class TestFileQuery(unittest.TestCase):
    def check_select_star_from_test(self, res: QueryResult):
        self.assertEqual(len(res.records), 3)

        for rec in res.records:
            self.assertEqual(len(rec), 3)

    def test_exec_query(self):
        fdb = FileDb("example/test.csv")
        res = fdb.exec_query("select * from test")

        self.check_select_star_from_test(res)

    def test_filesdir_no_trailing_slash(self):
        fdb = FileDb("example/data")
        res = fdb.exec_query("select * from test")

        self.check_select_star_from_test(res)

    def test_filesdir_trailing_slash(self):
        fdb = FileDb("example/data/")
        res = fdb.exec_query("select * from test")

        self.check_select_star_from_test(res)

    def test_multi_query(self):
        fdb = FileDb("example/data/")
        res = fdb.exec_many_queries(
            [
                "select * from test;",
                "select * from test1;",
                """
            select *
                from test t1
                inner join test1 t2
                on t1.col1 = t2.col1;
            """,
            ]
        )

        self.assertEqual(len(res), 3)

    def test_select_star_json(self):
        fdb = FileDb("example/json_test.json")
        res = fdb.exec_query("select * from json_test")

        self.assertEqual(res.records[0][0], 1)
        self.assertEqual(res.records[0][1], "test 1")
        self.assertEqual(res.records[0][2], 1.0)

    def test_select_struct_field(self):
        fdb = FileDb("example/json_test.json")
        res = fdb.exec_query("select nested.nest_id, nested.nest_val from json_test")

        self.assertEqual(res.records[0][0], 2)
        self.assertEqual(res.records[0][1], "nested test 1")

    def test_select_list_field(self):
        fdb = FileDb("example/json_test.json")
        res = fdb.exec_query("select list[1], list[2], list[3], list[4] from json_test")

        self.assertEqual(res.records[0][0], 1)
        self.assertEqual(res.records[0][1], 2)
        self.assertEqual(res.records[0][2], 3)
        self.assertEqual(res.records[0][3], 4)

    def test_json_list_file(self):
        fdb = FileDb("example/json_list_test.json")
        res = fdb.exec_query("select * from json_list_test")

        self.assertEqual(len(res.records), 3)

    # TODO add tests for joining JSON, CSV and parquet files
    def test_join_json_and_csv(self):
        fdb = FileDb("example/data/")
        res = fdb.exec_query(
            """
            select *
            from 
                test t1
                inner join test1 t2
                on t1.col1 = t2.col1;
        """
        )

        self.assertEqual(len(res.records), 2)

    def test_ndjson_file(self):
        fdb = FileDb("example/ndjson_test.ndjson")
        res = fdb.exec_query(
            "select id, value, nested.subid, nested.subval from ndjson_test"
        )

        self.assertEqual(len(res.records), 4)


class TestFileQueryCli(unittest.TestCase):
    #####################################################
    # tests for invalid arguments
    #####################################################

    def test_no_filename_or_filesdir(self):
        args = FileQueryArgs(
            filename=None,
            filesdir=None,
            query="select * from test",
            query_file=None,
            out_file=None,
            out_file_format=None,
            delimiter=None,
            editor=False,
        )

        err = validate_args(args)

        self.assertIsNotNone(err)

    def test_provide_filename_and_filesdir(self):
        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir="example/data",
            query="select * from test",
            query_file=None,
            out_file=None,
            out_file_format=None,
            delimiter=None,
            editor=False,
        )

        err = validate_args(args)

        self.assertIsNotNone(err)

    def test_no_query_or_query_file(self):
        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir=None,
            query=None,
            query_file=None,
            out_file=None,
            out_file_format=None,
            delimiter=None,
            editor=False,
        )

        err = validate_args(args)

        self.assertIsNotNone(err)

    def test_provide_query_and_query_file(self):
        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir=None,
            query="select * from test",
            query_file="example/queries/join.sql",
            out_file=None,
            out_file_format=None,
            delimiter=None,
            editor=False,
        )

        err = validate_args(args)

        self.assertIsNotNone(err)

    #####################################################
    # tests for handling arguments
    #####################################################

    def handle_args_single_out_file(self, args: FileQueryArgs, out_file: str):
        # call handle_args for creating an output file, check that the file exists, then delete the file
        handle_args(args)
        self.assertTrue(os.path.exists(out_file))

        # cleanup
        os.remove(out_file)

    def handle_args_multiple_out_files(self, args: FileQueryArgs):
        # call handle_args for creating multiple output files, check that each file exists, then delete the files
        handle_args(args)

        for file in args.out_file:
            self.assertTrue(os.path.exists(file))

            # cleanup
            os.remove(file)

    def test_single_output_file_default(self):
        out_file = "test_result.csv"

        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir=None,
            query="select * from test",
            query_file=None,
            out_file=[out_file],
            out_file_format=None,
            delimiter=None,
            editor=False,
        )

        self.handle_args_single_out_file(args, out_file)

    def test_single_output_file_csv(self):
        out_file = "test_result.csv"

        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir=None,
            query="select * from test",
            query_file=None,
            out_file=[out_file],
            out_file_format="csv",
            delimiter=None,
            editor=False,
        )

        self.handle_args_single_out_file(args, out_file)

    def test_single_output_file_parquet(self):
        out_file = "test_result.parquet"

        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir=None,
            query="select * from test",
            query_file=None,
            out_file=[out_file],
            out_file_format="parquet",
            delimiter=None,
            editor=False,
        )

        self.handle_args_single_out_file(args, out_file)

    def test_multiple_output_files_default(self):
        out_files = ["test_result1.csv", "test_result2.csv", "test_result3.csv"]

        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir=None,
            query="select * from test; select sum(col3) from test; select col1 from test where col1 = 1;",
            query_file=None,
            out_file=out_files,
            out_file_format=None,
            delimiter=None,
            editor=False,
        )

        self.handle_args_multiple_out_files(args)

    def test_multiple_output_files_csv(self):
        out_files = ["test_result1.csv", "test_result2.csv", "test_result3.csv"]

        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir=None,
            query="select * from test; select sum(col3) from test; select col1 from test where col1 = 1;",
            query_file=None,
            out_file=out_files,
            out_file_format="csv",
            delimiter=None,
            editor=False,
        )

        self.handle_args_multiple_out_files(args)

    def test_multiple_output_files_parquet(self):
        out_files = [
            "test_result1.parquet",
            "test_result2.parquet",
            "test_result3.parquet",
        ]

        args = FileQueryArgs(
            filename="example/test.csv",
            filesdir=None,
            query="select * from test; select sum(col3) from test; select col1 from test where col1 = 1;",
            query_file=None,
            out_file=out_files,
            out_file_format="parquet",
            delimiter=None,
            editor=False,
        )

        self.handle_args_multiple_out_files(args)


if __name__ == "__main__":
    unittest.main()

    # for one-off testing
    # fdb = FileDb('example/test.csv')
    # fdb.export_database('test')
    # res = fdb.exec_query('select * from test')

    # print(res)
