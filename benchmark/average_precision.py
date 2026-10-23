import json
import os

K = 5

# Carica risultati salvati
with open("benchmark/bench_save.json", "r", encoding="utf-8") as f:
    data = json.load(f)

bench_postgres = data["bench_postgres"]
bench_whoosh = data["bench_whoosh"]

# Carica le query (Q1..Q10)
with open("benchmark/Query_per_golden_list.json", "r", encoding="utf-8") as f:
    query_ids = list(json.load(f).keys())

# Gold Standard: {"Q1": ["Influenza", ...], "Q2": [...], ...} (titoli rilevanti)
# Con ~1M di documenti non si possono giudicare tutti a mano: il gold standard
# si costruisce con pooling, cioè giudicando solo l'unione dei top-k restituiti
# dai due motori per ogni query.
GOLDEN_PATH = "benchmark/golden_list.json"
if os.path.exists(GOLDEN_PATH):
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        GOLDEN_LIST = json.load(f)
else:
    print(f"Attenzione: {GOLDEN_PATH} non trovato, tutte le metriche saranno 0.\n")
    GOLDEN_LIST = {}


def golden(q):
    return set(GOLDEN_LIST.get(q, []))


def precision_at_k(result, gold, k=K):
    top = result[:k]
    return sum(1 for d in top if d in gold) / k


def recall_at_k(result, gold, k=K):
    if not gold:
        return 0.0
    return sum(1 for d in result[:k] if d in gold) / len(gold)


def f1_at_k(p, r):
    return 2 * p * r / (p + r) if (p + r) else 0.0


def average_precision(result, gold):
    total = 0.0
    rel_count = 0
    for i, doc in enumerate(result, start=1):
        if doc in gold:
            rel_count += 1
            total += rel_count / i
    return total / len(gold) if gold else 0.0


def evaluate(engine_results):
    """engine_results: lista di liste, nello stesso ordine di query_ids."""
    rows = {}
    for q, result in zip(query_ids, engine_results):
        gold = golden(q)
        p = precision_at_k(result, gold)
        r = recall_at_k(result, gold)
        rows[q] = {
            "P@5": round(p, 3),
            "R@5": round(r, 3),
            "F1@5": round(f1_at_k(p, r), 3),
            "AP": round(average_precision(result, gold), 3),
        }
    return rows


engines = {
    "Postgres": evaluate(bench_postgres),
    "Whoosh": evaluate(bench_whoosh),
}

for engine, rows in engines.items():
    print(f"\n{engine}:")
    for q, m in rows.items():
        print(f"  {q}: {m}")
    map_score = sum(m["AP"] for m in rows.values()) / len(rows)
    print(f"  MAP: {map_score:.3f}")