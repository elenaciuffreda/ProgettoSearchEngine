import pg8000    
import json

# connessione al db 
conn = pg8000.connect(
    user="postgres",
    password="postgres",
    database="search_medico",
    host="localhost",
    port=5432
)

cur = conn.cursor()

# carico i dati dal file JSONL
with open("../data/wiki_med_150.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        doc = json.loads(line)
        title = doc["title"]
        content = doc["text"]
        full_text = f"{title} {content}"

        cur.execute("""
            INSERT INTO docs (title, content, documento)
            VALUES (%s, %s, to_tsvector('italian', %s))
        """, (title, content, full_text))

conn.commit()
cur.close()
conn.close()

print("✅ Dati inseriti nel database PostgreSQL con successo!")
