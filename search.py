import subprocess
import sys
import louis.db.api as api
import louis.db as db
from microbench import MicroBench, MBReturnValue, MBFunctionCall
import pandas as pd


class Bench(MicroBench, MBFunctionCall, MBReturnValue):
    pass


outfile = "benchmarking/search_results.json"
commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
basic_bench = Bench(
    output_file=outfile, commit_version=commit, function_version="0.0.1"
)


def search(cursor, query):
    """Execute the SQL search function"""
    return api.search_from_text_query(cursor, query)


@basic_bench
def init_bench(query):
    """Initialize the benchmark by calling the function search"""
    connection = db.connect_db()
    with db.cursor(connection) as cursor:
        return search(cursor, query)


if __name__ == "__main__":
    """How to execute: python3 -m search.py query"""
    init_bench(" ".join(sys.argv[1:]))
    with open(outfile, "r") as result_file:
        print(pd.read_json(result_file, lines=True))
