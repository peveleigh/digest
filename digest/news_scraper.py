import feedparser
import json
import newspaper
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock
from time import sleep
from typing import List, Dict
from digest.db_handler import DatabaseHandler
from digest.news_summarizer import NewsSummarizer
from digest.models import NewsArticle


class NewsScraper:
    def __init__(self, db_url: str, api_key: str, model: str, user_agent: str, feeds_file: str):
        self.db_url = db_url
        self.api_key = api_key
        self.model = model
        self.feeds_file = feeds_file

        self.user_agent = user_agent

        # Initialize Summarizer
        self.summarizer = NewsSummarizer(self.api_key, self.model)

        # Constants for filtering
        self.URL_SKIP_PATTERNS = [
            "/livestory/","/video/","/sports/","/tv-shows/","/player/","/radio/",
            "/music/","/entertainment/","/liveblog/","/commentary/"
        ]
        self.URL_REQUIRE_PATTERNS = ["www.cbc.ca/news/"]

    def _should_skip(self, url: str) -> bool:
        """Internal logic to determine if a URL should be ignored."""
        if any(pattern in url for pattern in self.URL_SKIP_PATTERNS):
            return True
        return False

    def _get_article_urls(self, rss_url: str) -> List[str]:
        """Parses an RSS feed and returns a list of links."""
        headers = {
            'User-Agent': self.user_agent
        }
        # Use requests to get the data
        response = requests.get(rss_url, headers=headers, timeout=10)

        # Raise an error for bad status codes (4xx, 5xx)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return [entry.link for entry in feed.entries]

    def _fetch_article_data(self, article_url: str, category: str) -> NewsArticle:
        """Downloads, parses, and summarizes a single article."""
        article = newspaper.article(article_url)
        #summary = self.summarizer.summarize_single_article(article.title, article.text)
        return NewsArticle(
            url=article_url,
            title=article.title,
            content=article.text,
            summary=None,
            published=article.publish_date,
            scraped_at=datetime.now(),
            category=category
        )

    def _process_feed(self, rss_feed: Dict, db: DatabaseHandler, db_lock: Lock) -> bool:
        """Processes a single RSS feed. Returns True if any article was scraped."""
        rss_url = rss_feed['url']
        rss_category = rss_feed['category']

        print(f"Processing: {rss_url}")
        article_urls = self._get_article_urls(rss_url)
        feed_scraped = False

        for article_url in article_urls:
            if self._should_skip(article_url):
                continue

            with db_lock:
                exists = db.url_exists(article_url)

            if not exists:
                try:
                    data = self._fetch_article_data(article_url, rss_category)
                    with db_lock:
                        db.save_page(data)
                    print(f"[OK] {article_url}")
                    sleep(3)  # Rate limiting
                    feed_scraped = True
                except Exception as e:
                    print(f"[Error] {article_url}: {e}")

        return feed_scraped

    def run(self):
        """Main execution loop."""
        # Load feeds from the provided JSON filename
        with open(self.feeds_file, 'r') as file:
            rss_feeds = json.load(file)

        with DatabaseHandler(self.db_url) as db:
            db_lock = Lock()
            scraped = False

            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._process_feed, rss_feed, db, db_lock): rss_feed
                    for rss_feed in rss_feeds
                }

                for future in as_completed(futures):
                    try:
                        if future.result():
                            scraped = True
                    except Exception as e:
                        print(f"[Error] Feed failed: {e}")

            if not scraped:
                print("Nothing to scrape")
            db.commit()