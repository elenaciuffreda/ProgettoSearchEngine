def create_indexes(conn):
    cur = conn.cursor()
    # indicizza il tsvector su title+content
    cur.execute("""
      UPDATE docs
      SET documento = to_tsvector('italian', coalesce(title,'') || ' ' || coalesce(content,''));
    """)
    cur.execute("""
      CREATE INDEX IF NOT EXISTS idx_docs_documento
      ON docs
      USING GIN(documento);
    """)
    conn.commit(); cur.close()
    print("Indice full-text creato su docs.documento.")
