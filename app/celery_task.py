import json
import time
import os
from datetime import datetime,timedelta, date
from redis import Redis
from redbeat import RedBeatSchedulerEntry
from celery import Celery
from celery.schedules import crontab

from crawling import main
from asgiref.sync import async_to_sync


CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_REDBEAT_URL = os.getenv('CELERY_REDBEAT_URL', 'redis://redis:6379/1')

c_app = Celery('news_analyzer')

c_app.conf.update(
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

c_app.conf.redbeat_redis_url = CELERY_REDBEAT_URL
c_app.conf.redbeat_key_prefix = 'redbeat:'
c_app.conf.redbeat_lock_key = None 
c_app.conf.redbeat_lock_timeout = 60  

redis_parts = CELERY_REDBEAT_URL.split('/')
redis_db = int(redis_parts[-1]) if redis_parts[-1].isdigit() else 0
redis_host = redis_parts[2].split(':')[0]
redis_port = int(redis_parts[2].split(':')[1]) if ':' in redis_parts[2] else 6379

c_app.redbeat_redis = Redis(host=redis_host, port=redis_port, db=redis_db)


def crontab_to_string(crontab: crontab):
    try:
        hour = next(iter(crontab.hour))
        minute = next(iter(crontab.minute))
        return f" Scheduled at {str(hour)}:{str(minute).zfill(2)}h."
    except Exception as e:
        return f"Error crontab to string: {str(e)}"

def celery_schedule_task(url: str, start_date: date, end_date:date):
    # print(f"Entrando a celery_schedule_task .....")
    try:
        task_name = f"crawl-{url.replace('://', '-').replace('/', '-')}-{start_date}-to-{end_date}"
        entry = RedBeatSchedulerEntry(
            name=task_name,
            task='crawl_scheduled_task',  
            schedule=crontab(hour=12, minute=50),
            args=[url],
            kwargs={"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "task_name": task_name},
            options={'expires': (end_date + timedelta(days=1)).isoformat()},
            app=c_app,
        )

        print(f"Task '{task_name}' scheduled until {end_date}")
        entry.save()
        print(f"Entry saved: {entry}")
        
        return {
            "task_name": task_name,
            "url": url,
            "start_date": start_date,
            "end_date": end_date,
            "expires": end_date + timedelta(days=1),
            "message": f"Crawling scheduled daily at 12:00h from: {start_date} to {end_date}",
            "status": "scheduled"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Error programing the task"
        }


def get_scheduled_tasks():
    try:
        scheduler = c_app.redbeat_redis
        key_pattern = "redbeat:*"
        tasks = []
        print(f"Scheduler  {scheduler}::: Scheduler keys with pattern  {scheduler.keys(key_pattern)}")

        for key in scheduler.keys(key_pattern):
            entry_key = key.decode('utf-8')
            print(f"Processing key: {entry_key}")
            if ":lock:" in entry_key or entry_key.endswith(":last_run_at"):
                print(f"Ignoring lock or last_run_at key") 
                continue

            try:
                entry = RedBeatSchedulerEntry.from_key(entry_key, app=c_app)

                task_info = {
                    "task_name": entry.name,
                    "task": entry.task,
                    "args": entry.args,
                    "kwargs": entry.kwargs,
                    "options": entry.options,
                    "schedule": crontab_to_string(entry.schedule),
                    "last_run_at": str(entry.last_run_at) if entry.last_run_at else None,
                }

                tasks.append(task_info)

            except Exception as e:
                print(f"Error loading task {entry_key}: {e}")
                continue

        return tasks

    except Exception as e:
        return {"error": str(e), "message": "Error listing scheduled tasks"}
    
def delete_scheduled_task(task_name: str):
    try:
        redis_conn = c_app.redbeat_redis
        redbeat_key = f"redbeat:{task_name}"
        
        deleted = redis_conn.delete(redbeat_key)
        return {
            "task_name": task_name,
            "deleted": deleted == 1,
            "message": "Task eliminated" if deleted else "Task not found",
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Error deleting scheduled task"
        }


@c_app.task(name='crawl_scheduled_task')
def crawl_scheduled_task(url: str, start_date: str, end_date: str, task_name: str):
    today = datetime.now().date()

    print(f"----------------Starting Scheduled Crawl at {datetime.now()}----------------------")

    if datetime.strptime(start_date,"%Y-%m-%d").date() > today:
        # print(f"Start date {start_date} is after current day.")
        return {"message": f"Start date {start_date} is after current day. Task will not run."}
    if datetime.strptime(end_date,"%Y-%m-%d").date() < today:
        # print(f"End date {end_date} is after the current date. TASK EXPIRED")
        return {"message": f"End date {end_date} is after the current date. TASK EXPIRED"}
    try:
        result = async_to_sync(main)(url,task_name)
        #Esto se devuelve cuando termina la celerytask
        return {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
        }
    except Exception as e:
        print(f"Error in programmed crawling: {str(e)}")
        return {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }
        

@c_app.task
def crawl_task(url: str):
    print("----------------Starting Celery Crawl----------------------")
    result = async_to_sync(main)(url)
    return result
