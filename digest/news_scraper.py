import feedparser
import json
import newspaper
import os
import requests

from datetime import datetime
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
        summary = "..."
        return NewsArticle(
            url=article_url,
            title=article.title,
            content=article.text,
            summary=summary,
            published=article.publish_date,
            scraped_at=datetime.now(),
            category=category
        )

    def run(self):
        """Main execution loop."""
        # Load feeds from the provided JSON filename
        with open(self.feeds_file, 'r') as file:
            rss_feeds = json.load(file)

        with DatabaseHandler(self.db_url) as db:
            scraped = False
            for rss_feed in rss_feeds:
                rss_url = rss_feed['url']
                rss_category = rss_feed['category']
                print(f"Processing: {rss_url}")
                article_urls = self._get_article_urls(rss_url)
                

                for article_url in article_urls:
                    if self._should_skip(article_url):
                        continue
                    
                    if not db.url_exists(article_url):
                        try:
                            data = self._fetch_article_data(article_url, rss_category)
                            db.save_page(data)
                            print(f"[OK] {article_url}")
                            sleep(3)  # Rate limiting
                            scraped = True
                        except Exception as e:
                            print(f"[Error] {article_url}: {e}")
            if not scraped:
                print("Nothing to scrape")
            db.commit()

