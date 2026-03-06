import os

from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

from digest.app import scrape, summarize

from dotenv import load_dotenv

load_dotenv()

t_zone = os.getenv("TIMEZONE")
scrape_schedule_hour = os.getenv("SCRAPE_SCHEDULE_HOUR")
scrape_schedule_minute = os.getenv("SCRAPE_SCHEDULE_MINUTE")
summarize_schedule_hour = os.getenv("SUMMARIZE_SCHEDULE_HOUR")
summarize_schedule_minute = os.getenv("SUMMARIZE_SCHEDULE_MINUTE")

scheduler = BlockingScheduler(timezone=timezone(t_zone))

@scheduler.scheduled_job('cron', hour=scrape_schedule_hour, minute=scrape_schedule_minute)
def scrape_job():
    print("Starting scrape job...")
    scrape()

@scheduler.scheduled_job('cron', hour=summarize_schedule_hour, minute=summarize_schedule_minute)
def summarize_job():
    print("Starting summarize job...")
    summarize()

scheduler.start()