def create_indexes(conn):
    """
    Crea l'indice GIN sul tsvector (già calcolato in fase di inserimento).
    Idempotente: se l'indice esiste già non fa nulla.
    """
    cur = conn.cursor()
    # più memoria per la costruzione dell'indice su ~1M di documenti
    cur.execute("SET maintenance_work_mem = '1GB';")
    cur.execute("""
      CREATE INDEX IF NOT EXISTS idx_docs_documento
      ON docs
      USING GIN(documento);
    """)
    # statistiche aggiornate per il planner
    cur.execute("ANALYZE docs;")
    conn.commit()
    cur.close()
    print("Indice full-text creato su docs.documento.")