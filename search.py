# Name of this file: search.py
# Location: at the root of the project
# How to execute: python3 -m search.py query

import sys
import louis.db.api as api
import louis.db as db
from microbench import MicroBench
import pandas as pd

basic_bench = MicroBench()

# Execute the SQL search function 
@basic_bench
def search(cursor, query):
    return api.search_from_text_query(cursor, query)

if __name__ == '__main__':
    connection = db.connect_db()
    with db.cursor(connection) as cursor:
        results = search(cursor, ' '.join(sys.argv[1:]))
    print(results)
    print(pd.read_json(basic_bench.outfile.getvalue(), lines=True))