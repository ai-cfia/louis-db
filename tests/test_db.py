import os
import unittest
import pytest
import psycopg
import json
from psycopg.rows import dict_row

import dotenv
dotenv.load_dotenv()

def raise_error(message):
    raise SystemExit(message)

LOUIS_DSN = os.getenv("LOUIS_DSN") or raise_error("LOUIS_DSN is not set")
MATCH_THRESHOLD = 0.5
MATCH_COUNT = 10

class DBTest(unittest.TestCase):

    def execute(self, filename):
        query = open('sql/2023-07-19-weighted_search.sql').read()
        self.cursor.execute(query)

    def setUp(self):
        self.connection = psycopg.connect(LOUIS_DSN)
        self.cursor = self.connection.cursor(row_factory=dict_row)
        self.cursor.execute("SET search_path TO louis_v004, public")

    def tearDown(self):
        self.cursor.close()
        self.connection.close()

    def test_weighted_search(self):
        self.execute('sql/2023-07-19-modified-documents.sql')
        self.execute('sql/2023-07-19-weighted_search.sql')
        
        embeddings = json.load(open('tests/embeddings/president.json'))
        query = 'who is the president of the CFIA?'
        weights = json.dumps(
            {'similarity': 0.6, 'recency': 0.2, 'traffic': 0.0, 'current': 0.1})
        self.cursor.execute(
            "SELECT * FROM search(%s, %s::vector, %s::float, %s::integer, %s::jsonb)", (
                query, embeddings, MATCH_THRESHOLD, MATCH_COUNT, weights))
        results = self.cursor.fetchall()
        result = results[0]['search']
        self.assertEqual(
            result[0]['title'], 
            "Dr. Harpreet S. Kochhar - Canadian Food Inspection Agency")
        
        query_id = result[0]['query_id']
        self.cursor.execute("SELECT * FROM query where id = %s::uuid", (query_id,))
        result = self.cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['query'], query)
        result_embedding = json.loads(result[0]['embedding'])
        self.assertAlmostEqual(result_embedding[0], embeddings[0])
        self.assertEqual(len(result[0]['result']), MATCH_COUNT)

    def test_weighted_search_with_empty_query(self):
        self.execute('sql/2023-07-19-modified-documents.sql')
        self.execute('sql/2023-07-19-weighted_search.sql')
        
        weights = json.dumps({ 'recency': 0.4, 'traffic': 0.4, 'current': 0.2})
        self.cursor.execute(
            "SELECT * FROM search(%s, %s::vector, %s::float, %s::integer, %s::jsonb)", (
                None, None, MATCH_THRESHOLD, MATCH_COUNT, weights))
        result = self.cursor.fetchall()[0]['search']
        self.assertEqual(len(result), MATCH_COUNT, "Should return 10 results")
        urls = dict([(r['url'], True) for r in result])
        self.assertEqual(len(urls.keys()), MATCH_COUNT, "All urls should be unique")
    

    @unittest.skip("we have to re-chunk the documents using louis-crawler first")
    @pytest.mark.skip(
        reason="we have to re-chunk the documents using louis-crawler first")
    def test_every_crawl_doc_should_have_at_least_one_chunk(self):
        self.cursor.execute("""
            SELECT count(*) 
            FROM crawl LEFT JOIN chunk ON crawl.id = chunk.crawl_id 
            WHERE chunk.id IS NULL""")
        result = self.cursor.fetchall()
        self.assertEqual(
            result[0]['count'], 0, 
            "Every crawl doc should have at least one chunk")
    