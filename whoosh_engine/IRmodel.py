# whoosh_engine/IRmodel.py

import os, yaml
from whoosh import index
from whoosh.qparser import MultifieldParser
from whoosh.scoring import TF_IDF, BM25F

# Legge la config
base = os.path.dirname(__file__)
cfg  = yaml.safe_load(open(os.path.join(base, "config.yaml"), encoding="utf-8"))

INDEX_DIR = os.path.normpath(os.path.join(base, cfg["INDEX_DIR"]))
ix        = index.open_dir(INDEX_DIR)
parser    = MultifieldParser(["title", "content"], schema=ix.schema)

# TF-IDF standard
def search_tfidf(query_str, limit=10):
    with ix.searcher(weighting=TF_IDF()) as searcher:
        q = parser.parse(query_str)
        return [(r["title"], r.score) for r in searcher.search(q, limit=limit)]

# BM25 standard
def search_bm25(query_str, limit=10):
    with ix.searcher(weighting=BM25F()) as searcher:
        q = parser.parse(query_str)
        return [(r["title"], r.score) for r in searcher.search(q, limit=limit)]

# Weighted tramite BM25F con pesi campo da config
def search_weighted(query_str, limit=10):
    weights = cfg["RANKING"]["weights"]
    # Applica i pesi ai campi title e content
    weighting = BM25F(field_W=weights)
    with ix.searcher(weighting=weighting) as searcher:
        q = parser.parse(query_str)
        return [(r["title"], r.score) for r in searcher.search(q, limit=limit)]

# CLI di prova
if __name__ == "__main__":
    q = input("Query: ")
    print("\nTF-IDF:")
    for t, s in search_tfidf(q): print(f"{s:.3f}  {t}")
    print("\nBM25:")
    for t, s in search_bm25(q):  print(f"{s:.3f}  {t}")
    print("\nWeighted:")
    for t, s in search_weighted(q): print(f"{s:.3f}  {t}")



