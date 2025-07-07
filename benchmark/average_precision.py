import json

# Carica risultati salvati
with open("benchmark/bench_save.json", "r") as f:
    data = json.load(f)

bench_postgres = data["bench_postgres"]
bench_pylucene = data["bench_pylucene"]
bench_whoosh   = data["bench_whoosh"]

# Carica Golden List (titoli o ID definiti manualmente)
with open("benchmark/Query_per_golden_list.json", "r") as f:
    golden_queries = json.load(f)

# TODO: definire GOLDEN_LIST con i risultati attesi (titoli)
GOLDEN_LIST = {
    q: [] for q in golden_queries.keys()
}

# Calcola Average Precision per una query
def average_precision(result, golden):
    total = 0.0
    rel_count = 0
    for i, doc in enumerate(result, start=1):
        if doc in golden:
            rel_count +=1
            total += rel_count / i
    return total / len(golden) if golden else 0.0

# Calcola AP per ogni motore
def compute_ap(engine_results):
    ap_scores = {}
    for q, results in engine_results.items():
        ap_scores[q] = round(average_precision(results, GOLDEN_LIST[q]), 3)
    return ap_scores

# Esegui calcolo e stampa
aps = {
    'Postgres': compute_ap({q: bench_postgres[i] for i, q in enumerate(bench_postgres)}),
    'PyLucene': compute_ap({q: bench_pylucene[i] for i, q in enumerate(bench_pylucene)}),
    'Whoosh':   compute_ap({q: bench_whoosh[i]   for i, q in enumerate(bench_whoosh)})
}

print("Average Precision per motore:")
for engine, scores in aps.items():
    print(f"\n{engine}:")
    for q, ap in scores.items():
        print(f"  {q}: {ap}")