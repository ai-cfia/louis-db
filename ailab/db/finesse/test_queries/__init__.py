def get_random_chunk(cursor):
    query = """
        SELECT dc.score AS score, cr.id AS crawl_id, ch.id AS chunk_id, ch.title, cr.url AS crawl_url, ch.text_content, ch.text_content
        FROM Chunk ch
        INNER JOIN html_content_to_chunk hctc ON ch.id = hctc.chunk_id
        INNER JOIN html_content hc ON hctc.md5hash = hc.md5hash
        INNER JOIN crawl cr ON hc.md5hash = cr.md5hash
        INNER JOIN documents dc ON ch.id = dc.chunk_id
        WHERE dc.score > 0.0
        ORDER BY RANDOM()
        LIMIT 1;
    """
    cursor.execute(query)
    return cursor.fetchall()

def chunk_test_quality(cursor):
    query = """
        
    """
    cursor.execute(query)
    return cursor.fetchall()