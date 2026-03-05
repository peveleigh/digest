import argparse
import os
import sys

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
    # Using the context manager (__enter__ / __exit__) handles connection/closing
    with DatabaseHandler(db_url) as db:
        #print("Fetching unreviewed articles from the last 24 hours...")
        
        ns = NewsSummarizer(api_key,model)

        for category in ["world","local","business","technology"]:

            #print(category)
            articles = db.get_recent_unreviewed_articles(category,hours=24)
            
            if not articles:
                print("No new articles found.")
                continue

            article_titles = "\n".join([a.title for a in articles])
            
            summary = ns.summarize_title_list(article_titles)
            #summary = category
            send_gotify_notification(
                gotify_url,
                gotify_token,
                f"{category} news summary",
                summary,
                priority=5
            )

def main():
    # 1. Set up the argument parser
    parser = argparse.ArgumentParser(description="A tool to scrape data or summarize content.")
    
    # 2. Add a positional argument that accepts 'scrape' or 'summarize'
    parser.add_argument(
        "action", 
        choices=["scrape", "summarize"], 
        help="The function you want to run: 'scrape' or 'summarize'"
    )

    # 3. Parse the arguments from the command line
    args = parser.parse_args()

    # 4. Run the logic based on the input
    if args.action == "scrape":
        result = scrape()
        
    elif args.action == "summarize":
        result = summarize()

    else:
        print("Invalid argument")