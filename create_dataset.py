# create_dataset.py
"""
Script per creare il dataset medico da Wikipedia in formato JSONL.
Ogni riga del file di output contiene un documento con campi:
- title: titolo della pagina Wikipedia
- text: contenuto completo della pagina

Requisiti:
- pip install wikipedia tqdm
"""
import os
import json
from tqdm import tqdm
import wikipedia

# Cartella di destinazione
DIR = "data"
# File di output JSONL
OUTPUT_FILE = os.path.join(DIR, "wiki_med_dataset.jsonl")

# Lista di argomenti medici da estrarre
TOPICS = [
    "Influenza",
    "Diabete mellito",
    "Ipertensione arteriosa",
    "Bronchite",
    "Vaccinazione",
    "COVID-19",
    "Cancro",
    "Asma bronchiale",
    "Artrite reumatoide",
    "Osteoporosi",
    "Malaria",
    "Epilessia",
    "Sclerosi multipla",
    "Tubercolosi",
    "Depressione (malattia)",
    "Malattia di Alzheimer",
    "Infarto del miocardio",
    "Epatite C",
    "Morbo di Parkinson",
    "Anemia"
]


def create():
    """
    scarica pagine Wikipedia divisi per 'TOPICS'
    e salva come JSONL in data/wiki_med_dataset.jsonl
    """
    os.makedirs(DIR, exist_ok=True)
    wikipedia.set_lang("it")  # italiano

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for topic in tqdm(TOPICS, desc="Scaricamento Wikipedia"):  # barra di progresso
            try:
                page = wikipedia.page(topic, auto_suggest=False)
                doc = {
                    "title": page.title,
                    "text": page.content
                }
                out.write(json.dumps(doc, ensure_ascii=False) + "\n")
            except wikipedia.exceptions.DisambiguationError as e:
                # Prendi la prima opzione utile
                choice = e.options[0]
                try:
                    page = wikipedia.page(choice, auto_suggest=False)
                    doc = {"title": page.title, "text": page.content}
                    out.write(json.dumps(doc, ensure_ascii=False) + "\n")
                except Exception:
                    print(f"Impossibile risolvere disambiguazione per: {topic}")
            except Exception as ex:
                print(f"Errore su {topic}: {ex}")

    print(f"Dataset creato con {len(TOPICS)} documenti in {OUTPUT_FILE}")


if __name__ == '__main__':
    create()
