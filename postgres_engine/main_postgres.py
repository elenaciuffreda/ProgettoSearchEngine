import time
import os
import pg8000
from postgres_engine.database_config import DatabaseConfig
from postgres_engine.db_setup       import create_db, create_table
from postgres_engine.indexing       import create_indexes
from postgres_engine.search_engine  import SearchEngine

def db_connection(cfg):
    for _ in range(cfg.RECONNECT_ATTEMPTS):
        try:
            conn = pg8000.connect(
                user=cfg.DB_USER,
                password=cfg.DB_PASSWORD,
                host=cfg.IP_ADDRESS,
                port=cfg.PORT_NUMBER,
                database=cfg.DB_NAME      # pg8000 usa `database` anziché `dbname`
            )
            return conn
        except Exception:
            time.sleep(cfg.RECONNECT_INTERVAL)
    return None

def main_postgres():
    """Setup e interfaccia di ricerca per PostgreSQL."""
    cfg  = DatabaseConfig()
    conn = db_connection(cfg)
    if not conn:
        # Se non esiste il DB, lo creiamo
        create_db(cfg)
        conn = db_connection(cfg)

    # Creazione tabella e indici full-text
    create_table(conn)
    create_indexes(conn)

    # Entry-point per la ricerca
    engine = SearchEngine(cfg, conn)
    print("Scegli ranking: 1) TF-IDF   2) BM25   (invio per uscire)")
    while True:
        choice = input(">> ").strip()
        if choice not in ('1', '2'):
            break
        query = input("Query: ").strip()
        # Scegli la funzione di ricerca
        if choice == '1':
            results = engine.tfidf_search(query)
        else:
            results = engine.bm25_search(query)
        for title, score in results:
            print(f"{score:.3f}  {title}")

    conn.close()

if __name__ == '__main__':
    main_postgres()
