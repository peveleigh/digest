import os
import psycopg2

from digest.models import NewsArticle

class DatabaseHandler:
    def __init__(self, db_url: str = None):
        self.db_url = db_url
        self.conn = None

    def connect(self):
        """Creates a connection to the database."""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(self.db_url)

    def init_db(self):
        """Initializes the schema if it doesn't exist."""
        with self._cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS news_articles (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    summary TEXT DEFAULT NULL,
                    published TIMESTAMP DEFAULT NULL,
                    scraped_at TIMESTAMP DEFAULT NOW(),
                    reviewed BOOLEAN DEFAULT FALSE,
                    category TEXT DEFAULT NULL
                )
            """)
        self.conn.commit()

    def save_page(self, article: NewsArticle):
        """Inserts or updates page data."""
        query = """
            INSERT INTO news_articles (url, title, content, summary, published, scraped_at, category)
            VALUES (%(url)s, %(title)s, %(content)s, %(summary)s, %(published)s, %(scraped_at)s, %(category)s)
            ON CONFLICT (url) DO UPDATE
                SET title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    summary = EXCLUDED.summary,
                    published = EXCLUDED.published,
                    scraped_at = EXCLUDED.scraped_at,
                    category = EXCLUDED.category
        """
        try:
            with self._cursor() as cur:
                cur.execute(query, article.to_dict())
        except psycopg2.Error as e:
            self.conn.rollback()
            raise
        
    def commit(self):
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None

    def url_exists(self, url: str) -> bool:
        """Checks if a URL already exists in the database."""
        query = "SELECT 1 FROM news_articles WHERE url = %s LIMIT 1;"
        with self._cursor() as cur:
            cur.execute(query, (url,))
            return cur.fetchone() is not None

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_url)
        return self

    def __exit__(self, *args):
        self.close()

    def _cursor(self):
        """Returns a cursor, ensuring a connection exists."""
        if not self.conn or self.conn.closed:
            raise RuntimeError("Not connected. Use 'with DatabaseHandler() as db:' or call connect() first.")
        return self.conn.cursor()

    def get_articles_without_summary(self):
        """
        Yields NewsArticle objects where summary IS NULL.
        Uses a named server-side cursor to prevent memory overload.
        """
        query = "SELECT url, title, content, summary, published, scraped_at, category FROM news_articles WHERE summary IS NULL"
        
        with self._cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()  # Fetch all results into Python memory

        for row in rows:
            # Assuming NewsArticle has a constructor or a from_dict method
            yield NewsArticle(
                url=row[0],
                title=row[1],
                content=row[2],
                summary=row[3],
                published=row[4],
                scraped_at=row[5],
                category=row[6]
            )

    def get_recent_articles(self, category: str, hours: int = 12):
        """
        Fetches articles by category published within the last X hours 
        that haven't been reviewed.
        """
        query = """
            SELECT url, title, content, summary, published, scraped_at, category
            FROM news_articles
            WHERE published >= NOW() - INTERVAL '%s hours'
            AND reviewed = FALSE
            AND category = %s
        """
        
        with self._cursor() as cur:
            # We pass (hours, category) as a tuple to the execute method
            cur.execute(query, (hours, category))
            rows = cur.fetchall()
            
        articles = []
        for row in rows:
            articles.append(NewsArticle(
                url=row[0],
                title=row[1],
                content=row[2],
                summary=row[3],
                published=row[4],
                scraped_at=row[5],
                category=row[6]
            ))
        return articles