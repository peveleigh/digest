import psycopg2

DATABASE_URL="postgres://pgadmin:Tck82Xqz8Zh5@192.168.2.105:5432/pg_database_1"

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                url TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                published TIMESTAMP DEFAULT NULL,
                scraped_at TIMESTAMP DEFAULT NOW(),
                reviewed BOOLEAN DEFAULT FALSE,
                category TEXT DEFAULT NULL
            )
        """)
    conn.commit()

def run():
    conn = get_db()
    init_db(conn)
    conn.close()

run()