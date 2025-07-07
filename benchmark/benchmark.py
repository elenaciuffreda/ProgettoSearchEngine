import json
from postgres_engine.main_postgres import SearchEngine as PgEngine, DatabaseConfig
from pylucene_engine.pylucene_IR import search as pylucene_search, build_index as pylucene_build
from whoosh_engine.IRmodel import search_weighted as whoosh_search, build_index as whoosh_build

# Carica query tecniche
with open("benchmark/Query_per_golden_list.json", "r") as f:
    queries = list(json.load(f).values())

# 1) PostgreSQL
db_cfg = DatabaseConfig()
pg = PgEngine(db_cfg)
bench_postgres = []
for q in queries:
    results = [title for title, _ in pg.tfidf_search(q)]
    bench_postgres.append(results)

# 2) PyLucene
pylucene_build()
bench_pylucene = []
for q in queries:
    bench_pylucene.append([t for t, _ in pylucene_search(q)])

# 3) Whoosh
whoosh_build()
bench_whoosh = []
for q in queries:
    bench_whoosh.append([t for t, _ in whoosh_search(q)])

# Salva i risultati
with open("benchmark/bench_save.json", "w") as f:
    json.dump({
        "bench_postgres": bench_postgres,
        "bench_pylucene": bench_pylucene,
        "bench_whoosh": bench_whoosh
    }, f, indent=4)

print("Benchmark completato e salvato in benchmark/bench_save.json")