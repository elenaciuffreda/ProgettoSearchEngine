import time, os, psycopg2
from database_config import DatabaseConfig
from db_setup     import create_db, create_table
from indexing     import create_indexes
from search_engine import SearchEngine

def db_connection(cfg):
    for i in range(cfg.RECONNECT_ATTEMPTS):
        try:
            conn = psycopg2.connect(
              dbname=cfg.DB_NAME,
              user=cfg.DB_USER,
              password=cfg.DB_PASSWORD,
              host=cfg.IP_ADDRESS,
              port=cfg.PORT_NUMBER
            )
            return conn
        except:
            time.sleep(cfg.RECONNECT_INTERVAL)
    return None

if __name__ == '__main__':
    cfg  = DatabaseConfig()
    conn = db_connection(cfg)
    if not conn:
        create_db(cfg)
        conn = db_connection(cfg)
    create_table(conn)
    create_indexes(conn)

    engine = SearchEngine(cfg, conn)
    print("Scegli ranking: 1) TF-IDF  2) BM25  (invio per uscire)")
    while True:
        choice = input(">> ")
        if choice not in ('1','2'): break
        query  = input("Query: ")
        fn     = engine.tfidf_search if choice=='1' else engine.bm25_search
        for title, rank in fn(query):
            print(f"{rank:.3f}  {title}")
    conn.close()
