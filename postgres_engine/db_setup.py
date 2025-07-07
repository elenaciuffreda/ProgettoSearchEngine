import psycopg2

def create_db(cfg):
    conn = psycopg2.connect(dbname='postgres',
                            user=cfg.DB_USER,
                            password=cfg.DB_PASSWORD,
                            host=cfg.IP_ADDRESS,
                            port=cfg.PORT_NUMBER)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {cfg.DB_NAME};")
    cur.close(); conn.close()
    print(f"Database {cfg.DB_NAME} creato.")

def create_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS docs (
          id SERIAL PRIMARY KEY,
          title TEXT,
          content TEXT,
          documento TSVECTOR
        );
    """)
    conn.commit()
    cur.close()
    print("Tabella docs creata.")
