import json
from postgres_engine.main_postgres import SearchEngine as PgEngine, DatabaseConfig
from whoosh_engine.IRmodel import search_weighted as whoosh_search

# NOTA: gli indici NON vengono ricostruiti qui. Con ~1M di documenti
# l'indicizzazione richiede molto tempo: esegui prima `python main.py`
# (oppure gli script di indicizzazione dei singoli motori).

# Carica query tecniche
with open("benchmark/Query_per_golden_list.json", "r") as f:
    queries = list(json.load(f).values())

# 1) PostgreSQL
db_cfg = DatabaseConfig()
pg = PgEngine(db_cfg)
bench_postgres = []
for q in queries:
    bench_postgres.append([title for title, _ in pg.tfidf_search(q)])

# 2) Whoosh
bench_whoosh = []
for q in queries:
    bench_whoosh.append([title for title, _ in whoosh_search(q)])

# Salva i risultati
with open("benchmark/bench_save.json", "w") as f:
    json.dump({
        "bench_postgres": bench_postgres,
        "bench_whoosh": bench_whoosh
    }, f, indent=4, ensure_ascii=False)

print("Benchmark completato e salvato in benchmark/bench_save.json")