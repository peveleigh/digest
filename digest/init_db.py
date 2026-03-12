import psycopg2

from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(db_url)

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

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news_summaries (
                id SERIAL PRIMARY KEY,
                summary TEXT NOT NULL,
                summary_date TIMESTAMP NOT NULL,
                category TEXT NOT NULL
            )
        """)
    conn.commit()


def run():
    conn = get_db()
    init_db(conn)
    conn.close()

run()