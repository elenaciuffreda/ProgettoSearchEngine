import pg8000

class SearchEngine:
    def __init__(self, cfg, conn, limit=10):
        self.conn  = conn
        self.limit = limit

    def tfidf_search(self, raw_query):
        return self._search(raw_query, method='ts_rank')

    def bm25_search(self, raw_query):
        return self._search(raw_query, method='ts_rank_cd')

    def _search(self, raw_query, method):
        q = raw_query.replace(' ', ' & ')
        sql = f"""
          SELECT title, {method}(documento, plainto_tsquery('italian', %s)) AS rank
          FROM docs
          WHERE documento @@ plainto_tsquery('italian', %s)
          ORDER BY rank DESC
          LIMIT {self.limit};
        """
        cur = self.conn.cursor()
        cur.execute(sql, (q, q))
        results = cur.fetchall()
        cur.close()
        return results
