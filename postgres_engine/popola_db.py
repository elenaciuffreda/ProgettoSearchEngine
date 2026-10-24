import json
import os
from tqdm import tqdm

# File prodotto da create_dataset.py (percorso relativo alla radice del progetto)
DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "wiki_med_dataset.jsonl"
)
BATCH_SIZE = 200


def _clean(s):
    # PostgreSQL non accetta il carattere NUL nei campi di testo
    return (s or "").replace("\x00", "")


def _insert_batch(conn, batch):
    """Inserisce un blocco di (title, content) calcolando subito il tsvector."""
    sql = (
        "INSERT INTO docs (title, content, documento) "
        "SELECT t, c, to_tsvector('italian', t || ' ' || c) "
        "FROM (VALUES " + ",".join(["(%s::text, %s::text)"] * len(batch)) + ") AS v(t, c)"
    )
    params = [value for pair in batch for value in pair]
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    cur.close()


def populate_db(conn, path=DATA_FILE, batch_size=BATCH_SIZE):
    """
    Carica il JSONL nella tabella docs a blocchi (commit a ogni blocco).

    Riprendibile: le righe già presenti in tabella vengono saltate, quindi se il
    caricamento si interrompe basta rilanciarlo. Se il file è stato rigenerato,
    svuota prima la tabella con `TRUNCATE docs;`.
    """
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM docs")
    already = cur.fetchone()[0]
    cur.close()

    if already:
        print(f"docs contiene già {already} documenti: riprendo da lì.")

    batch = []
    inserted = 0
    with open(path, "r", encoding="utf-8") as f:
        for n, line in enumerate(tqdm(f, desc="Caricamento PostgreSQL")):
            if n < already or not line.strip():
                continue
            doc = json.loads(line)
            batch.append((_clean(doc["title"]), _clean(doc["text"])))
            if len(batch) >= batch_size:
                _insert_batch(conn, batch)
                inserted += len(batch)
                batch = []
    if batch:
        _insert_batch(conn, batch)
        inserted += len(batch)

    print(f"Inseriti {inserted} nuovi documenti (totale: {already + inserted}).")