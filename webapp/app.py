import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify
import time

from postgres_engine.database_config import DatabaseConfig
from postgres_engine.main_postgres   import db_connection
from postgres_engine.search_engine   import SearchEngine as PgSearchEngine

import whoosh_engine.IRmodel as WhooshIR

app = Flask(__name__)

# ── connessione PostgreSQL (una sola, tenuta aperta) ─────────────────────────
_pg_engine = None

def get_pg_engine():
    global _pg_engine
    if _pg_engine is None:
        cfg  = DatabaseConfig()
        conn = db_connection(cfg)
        if conn:
            _pg_engine = PgSearchEngine(cfg, conn)
    return _pg_engine


# ── route principale ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    query   = request.args.get("q", "").strip()
    engine  = request.args.get("engine", "postgres")   # postgres | whoosh
    ranking = request.args.get("ranking", "bm25")       # bm25 | tfidf  (solo postgres)
    limit   = int(request.args.get("limit", 10))

    if not query:
        return jsonify({"results": [], "time_ms": 0, "query": query})

    t0 = time.perf_counter()

    results = []
    error   = None

    try:
        if engine == "postgres":
            pg = get_pg_engine()
            if pg is None:
                raise RuntimeError("Impossibile connettersi a PostgreSQL.")
            pg.limit = limit
            if ranking == "tfidf":
                raw = pg.tfidf_search(query)
            else:
                raw = pg.bm25_search(query)
            results = [{"title": r[0], "score": round(float(r[1]), 4)} for r in raw]

        elif engine == "whoosh":
            raw     = WhooshIR.search_weighted(query, limit=limit)
            results = [{"title": t, "score": round(float(s), 4)} for t, s in raw]

    except Exception as e:
        error = str(e)

    elapsed = round((time.perf_counter() - t0) * 1000, 1)

    return jsonify({
        "query":    query,
        "engine":   engine,
        "ranking":  ranking,
        "results":  results,
        "time_ms":  elapsed,
        "error":    error,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

