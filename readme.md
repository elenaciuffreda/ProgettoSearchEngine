**📚 Progetto Gestione dell’Informazione - MediLens**


**Anno Accademico:** 2024/2025


**Corso:** Gestione dell’Informazione – Progetto Full-Text Search


**Studentessa:** Elena Maria Ciuffreda (Matricola: 119325)

---

## 🔎 Descrizione

Questo progetto ha l’obiettivo di implementare e confrontare tre motori di ricerca full-text applicati a un dataset di documenti medici:

1. **PostgreSQL**: utilizzo di `tsvector`/`tsquery` e ranking con `ts_rank_cd` (BM25-like) o `ts_rank` (TF–IDF).
2. **PyLucene** (in Docker): configurazione con `ItalianAnalyzer` e ranking BM25 o Classic (TF–IDF).
3. **Whoosh** (pure Python): `ItalianAnalyzer` con TF–IDF e variante weighted sui campi.

Ogni motore supporta query su parole chiave e su campi specifici, restituendo risultati ordinati per pertinenza.

---

## 📂 Struttura del Progetto

```
ProgettoSearchEngine/
├── data/
│   └── wiki_med_150.jsonl         # Dataset medico in formato JSONL
├── create_dataset.py             # Script per scaricare pagine Wikipedia (ITA)
├── main.py                       # Entry-point: setup e interfaccia CLI
├── postgres_engine/
│   ├── postgres.json             # Configurazione del database
│   ├── database_config.py
│   ├── db_setup.py
│   ├── indexing.py
│   ├── main_postgres.py
│   └── search_engine.py
├── whoosh_engine/
│   ├── config.yaml
│   ├── index.py
│   └── IRmodel.py
├── pylucene_engine/
│   └── pylucene_IR.py            # Script PyLucene (container)
├── benchmark/
│   ├── Query_per_golden_list.json
│   ├── bench_save.json
│   ├── benchmark.py
│   └── average_precision.py
└── README.md                     # Questo file
```

---

## ⚙️ Prerequisiti

* **Python 3.9** (consigliato in virtualenv)
* **pip**
* **PostgreSQL** & **pgAdmin** (o accesso via `psql`)
* **Docker Desktop** (necessario per PyLucene)
* Connessione Internet (per `create_dataset.py`)

---

## 🛠️ Installazione

1. **Clonare il repository**

   ```bash
   git clone https://tuo-repo-url.git
   cd ProgettoSearchEngine
   ```

2. **Creare e attivare un virtual environment**

   ```
   python -m venv venv
   # Windows (PowerShell/cmd.exe)
   .\venv\Scripts\activate                                #o \venv\bin\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Installare le dipendenze**

   ```
   pip install -r requirements.txt
   ```

4. **Popolare il dataset**
   Se non è già presente:

   ```
   python create_dataset.py
   ```

---

## 🚀 Utilizzo

### 1. Setup e indicizzazione

Eseguire lo script principale:

```
python main.py
```

Verranno create automaticamente le tabelle/indici per PostgreSQL, PyLucene (via Docker) e Whoosh.

### 2. Interfaccia di ricerca

Al termine del setup, verrà mostrato un menu interattivo:

1. Cerca con **PostgreSQL**
2. Cerca con **PyLucene**
3. Cerca con **Whoosh**
4. Esci

---

## 🐘 PostgreSQL

1. Configurare `postgres_engine/postgres.json` con le vostre credenziali:

   ```json
   {
     "NETWORK_SETTINGS": {
       "IP_ADDRESS": "localhost",
       "PORT_NUMBER": 5432
     },
     "DATABASE_SETTINGS": {
       "DB_USER": "postgres",
       "DB_PASSWORD": "<password>",
       "DB_NAME": "search_medico"
     }
   }
   ```

2. Avviare il motore PostgreSQL:

   ```
   python postgres_engine/main_postgres.py
   ```

   oppure tramite `python main.py` selezionando l’opzione 1.

---

## 🐍 Whoosh

1. La configurazione si trova in `whoosh_engine/config.yaml`.
2. Creazione indice automatica:

   ```
   python whoosh_engine/index.py
   ```
3. Esempio di ricerca:

   ```
   python whoosh_engine/IRmodel.py
   ```

---

## 🐳 PyLucene (Docker)

Per semplificare i binding Java su Windows, utilizziamo un container Docker:

1. **Scaricare l’immagine**

   ```
   docker pull coady/pylucene
   ```

2. **Avviare il container** (da root del progetto):

   ```
   docker run -it \
     --name gestinfo \
     -v /path/to/ProgettoSearchEngine:/workspace \
     -w /workspace/pylucene_engine \
     coady/pylucene bash
   ```

3. **Dentro il container**:

   * Installare dipendenze Python (solo la prima volta):

     ```
     pip install pyyaml pg8000 whoosh tqdm wikipedia
     ```
   * Eseguire lo script PyLucene:

     ```
     python pylucene_IR.py
     ```
   * Selezionare un’opzione:

     1. Indicizzazione → crea `lucene_index/`
     2. Ricerca → es. `influenza AND sintomi`

---

## 📊 Benchmark

1. Definire le query in `benchmark/Query_per_golden_list.json`.
2. Eseguire il benchmark:

   ```
   python benchmark/benchmark.py
   ```

   I risultati verranno salvati in `benchmark/bench_save.json`.
3. Calcolare le metriche:

   ```
   python benchmark/average_precision.py
   ```

**Metriche calcolate**:

* Precision\@5
* Recall\@5
* F1\@5
* Average Precision (AP)
* Mean Average Precision (MAP)
