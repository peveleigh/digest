import os

from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

from digest.app import scrape, summarize

from dotenv import load_dotenv

load_dotenv()

t_zone = os.getenv("TIMEZONE")
scrape_schedule_hour = int(os.getenv("SCRAPE_SCHEDULE_HOUR"))
scrape_schedule_minute = os.getenv("SCRAPE_SCHEDULE_MINUTE")
summarize_schedule_hour = int(os.getenv("SUMMARIZE_SCHEDULE_HOUR"))
summarize_schedule_minute = os.getenv("SUMMARIZE_SCHEDULE_MINUTE")

scrape_hours = f"{scrape_schedule_hour},{(scrape_schedule_hour + 12) % 24}"
summarize_hours = f"{summarize_schedule_hour},{(summarize_schedule_hour + 12) % 24}"

scheduler = BlockingScheduler(timezone=timezone(t_zone))

@scheduler.scheduled_job('cron', hour=scrape_hours, minute=scrape_schedule_minute)
def scrape_job():
    print("Starting scrape job...")
    scrape()

@scheduler.scheduled_job('cron', hour=summarize_hours, minute=summarize_schedule_minute)
def summarize_job():
    print("Starting summarize job...")
    summarize()

scheduler.start()