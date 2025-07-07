import os, json, yaml
from whoosh.fields import Schema, TEXT
from whoosh import index

# Carica la configurazione
cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "config.yaml"), encoding="utf-8"))

# Usa le chiavi root-level
DATA_DIR  = os.path.normpath(os.path.join(os.path.dirname(__file__), cfg["DATA_DIR"]))
INDEX_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), cfg["INDEX_DIR"]))


def build_index():
    # Definisci schema con boost neutro (pesi applicati in IRmodel.py)
    schema = Schema(
        title=TEXT(stored=True),
        content=TEXT(stored=True)
    )

    # Crea o apri indice
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
        ix = index.create_in(INDEX_DIR, schema)
    else:
        ix = index.open_dir(INDEX_DIR)

    writer = ix.writer()
    # Indicizza tutti i documenti
    path = os.path.join(DATA_DIR, "wiki_med_150.jsonl")
    with open(path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            writer.add_document(
                title=doc["title"],
                content=doc["text"]
            )
    writer.commit()
    print("✅ Whoosh: indicizzazione completata.")

if __name__ == "__main__":
    build_index()
