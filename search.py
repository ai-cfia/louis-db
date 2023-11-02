import subprocess
import sys
import logging
import louis.db.api as api
import louis.db as db
from microbench import MicroBench, MBReturnValue, MBFunctionCall
import pandas as pd


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Bench(MicroBench, MBFunctionCall, MBReturnValue):
    pass


OUTFILE = "benchmarking/search_results.json"
commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
basic_bench = Bench(
    output_file=OUTFILE, commit_version=commit, function_version="0.0.1"
)

@basic_bench
def init_bench(query):
    """Initialize the benchmark by calling the function search"""
    connection = db.connect_db()
    with db.cursor(connection) as cursor:
        return api.search_from_text_query(cursor, query)


if __name__ == "__main__":
    """Execute the sql search function with the query passed as an argument. 
    How to execute: python3 -m search.py query"""
    query = " ".join(sys.argv[1:])  
    logging.debug(f"Query is: {query}")
    init_bench(query)
    with open(OUTFILE, "r") as result_file:
        print(pd.read_json(result_file, lines=True))