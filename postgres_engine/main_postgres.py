import time
import pg8000
from postgres_engine.database_config import DatabaseConfig
from postgres_engine.db_setup       import create_db, create_table
from postgres_engine.indexing       import create_indexes
from postgres_engine.popola_db      import populate_db
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


def setup_postgres():
    """
    Setup completo e idempotente: crea database e tabella se mancano,
    carica i documenti non ancora presenti e crea l'indice GIN.
    Non è interattivo: si può rilanciare senza rifare il lavoro già fatto.
    """
    cfg  = DatabaseConfig()
    conn = db_connection(cfg)
    if not conn:
        # Se non esiste il DB, lo creiamo
        create_db(cfg)
        conn = db_connection(cfg)

    create_table(conn)
    populate_db(conn)
    create_indexes(conn)
    conn.close()


def search_postgres():
    """Interfaccia di ricerca interattiva (presuppone che il setup sia stato fatto)."""
    cfg  = DatabaseConfig()
    conn = db_connection(cfg)
    if not conn:
        print("Impossibile connettersi a PostgreSQL.")
        return

    engine = SearchEngine(cfg, conn)
    print("Scegli ranking: 1) TF-IDF   2) BM25   (invio per uscire)")
    while True:
        choice = input(">> ").strip()
        if choice not in ('1', '2'):
            break
        query = input("Query: ").strip()
        if choice == '1':
            results = engine.tfidf_search(query)
        else:
            results = engine.bm25_search(query)
        for title, score in results:
            print(f"{score:.3f}  {title}")

    conn.close()


def main_postgres():
    """Setup + ricerca (per l'esecuzione diretta del modulo)."""
    setup_postgres()
    search_postgres()


if __name__ == '__main__':
    main_postgres()