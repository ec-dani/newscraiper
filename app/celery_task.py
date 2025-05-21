import time
import os
from celery import Celery
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from pymongo import MongoClient

from crawl4AI import main
from asgiref.sync import async_to_sync


c_app = Celery('news_analyzer')

c_app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
)



@c_app.task
def crawl_task(url: str):
    print("----------------Starting Celery Crawl----------------------")
    result = async_to_sync(main)(url)
    tasks= c_app.control.inspect().registered_tasks()
    print(f"Tasks registered: {tasks}")
    return result
