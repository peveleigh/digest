from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

from digest.app import scrape, summarize

scheduler = BlockingScheduler(timezone=timezone("America/St_Johns"))

@scheduler.scheduled_job('cron', hour=17, minute=40)
def scrape_job():
    print("Starting scrape job...")
    scrape()

@scheduler.scheduled_job('cron', hour=17, minute=45)
def summarize_job():
    print("Starting scrape job...")
    summarize()


scheduler.start()