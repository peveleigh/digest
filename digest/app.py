import argparse
import os
import sys

from datetime import datetime

from digest.db_handler import DatabaseHandler
from digest.gotify import send_gotify_notification
from digest.news_scraper import NewsScraper
from digest.news_summarizer import NewsSummarizer

from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
api_key = os.getenv("API_KEY")
model = os.getenv("MODEL")
user_agent = os.getenv("USER_AGENT")
gotify_url = os.getenv("GOTIFY_URL")
gotify_token = os.getenv("GOTIFY_TOKEN")


feeds_file = "feeds.json"

def scrape():
    scraper = NewsScraper(
        db_url,
        api_key,
        model,
        user_agent,
        feeds_file
    )
    
    scraper.run()

def summarize():

    with DatabaseHandler(db_url) as db:
        
        ns = NewsSummarizer(api_key,model)

        for category in ["local","business","world"]:

            articles = db.get_recent_articles(category,hours=12)
            previous_summaries = db.get_previous_summaries(category)

            if not articles:
                continue
            else:
                news = ""
                for a in articles:
                    news = news + f"Title: {a.title} \n"
                    news = news + f"Content: {a.content} \n"
                    news = news + "---\n"
                news = news[:-5]
                summary = ns.summarize_article_list(news,previous_summaries)

            send_gotify_notification(
                gotify_url,
                gotify_token,
                f"{category} news summary",
                summary,
                priority=5
            )

            db.save_summary(summary,datetime.now(),category)
            db.commit()

def main():
    parser = argparse.ArgumentParser(description="A tool to scrape data or summarize content.")
    
    parser.add_argument(
        "action", 
        choices=["scrape", "summarize"], 
        help="The function you want to run: 'scrape' or 'summarize'"
    )

    args = parser.parse_args()

    if args.action == "scrape":
        result = scrape()
        
    elif args.action == "summarize":
        result = summarize()

    else:
        print("Invalid argument")