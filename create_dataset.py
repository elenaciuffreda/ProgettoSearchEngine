# create_dataset.py
"""
Crea il dataset in formato JSONL a partire da Wikipedia italiana
(dump wikimedia/wikipedia su Hugging Face, config 20231101.it).

Ogni riga del file di output contiene un documento con campi:
- title: titolo della pagina Wikipedia
- text: contenuto della pagina

Lo schema e il nome del file sono gli stessi di prima, quindi gli
indicizzatori esistenti (PostgreSQL, Whoosh) non vanno modificati.

Il dataset viene letto in streaming: non serve scaricare tutto il dump
prima, e il file di output cresce man mano.

Requisiti:
- pip install datasets tqdm
"""
import os
import json
from tqdm import tqdm
from datasets import load_dataset

# Cartella e file di output
DIR = "data"
OUTPUT_FILE = os.path.join(DIR, "wiki_med_dataset.jsonl")

# Numero di documenti desiderato (ordine del milione)
N_DOCS = 1_000_000
# Scarta le pagine troppo corte (stub, redirect, pagine di disambiguazione)
MIN_CHARS = 500
# Tronca i testi molto lunghi per contenere la dimensione dell'indice (None = nessun limite)
MAX_CHARS = 20_000

HF_DATASET = "wikimedia/wikipedia"
HF_CONFIG = "20231101.it"


def create(n_docs=N_DOCS):
    """
    Legge Wikipedia italiana in streaming e salva fino a n_docs documenti
    come JSONL in data/wiki_med_dataset.jsonl
    """
    os.makedirs(DIR, exist_ok=True)

    stream = load_dataset(HF_DATASET, HF_CONFIG, split="train", streaming=True)

    written = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        with tqdm(total=n_docs, desc="Creazione dataset") as pbar:
            for row in stream:
                text = (row.get("text") or "").strip()
                if len(text) < MIN_CHARS:
                    continue
                if MAX_CHARS:
                    text = text[:MAX_CHARS]

                doc = {"title": row["title"], "text": text}
                out.write(json.dumps(doc, ensure_ascii=False) + "\n")

                written += 1
                pbar.update(1)
                if written >= n_docs:
                    break

    print(f"Dataset creato con {written} documenti in {OUTPUT_FILE}")
    if written < n_docs:
        print(f"Attenzione: trovati solo {written} documenti su {n_docs} richiesti. "
              f"Prova ad abbassare MIN_CHARS.")


if __name__ == '__main__':
    create()