import asyncio
from typing import Dict
from crawl4ai import AsyncWebCrawler
from celery.result import AsyncResult
from celery import current_app
from datetime import datetime, timedelta,date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from celery_task import celery_schedule_task, get_scheduled_tasks,delete_scheduled_task
from mongodb import get_task_articles


app = FastAPI(
    title="News Analyzer API",
    description="API para analizar noticias de periódicos digitales",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers

@app.get("/")
async def root():
    return {"message": "NewsScrAIper API"}

@app.post("/schedule/add_task")
async def schedule_task(url: str, start_date: date, end_date: date):
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be prior to the end date.")
        
        if start_date < datetime.now().date():
            raise HTTPException(status_code=400, detail="start date must be prior to the current date.")
        # print("VOY PA CELERY")
        task= celery_schedule_task(url, start_date, end_date)
        return task
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedule/list_tasks")
async def list_scheduled_tasks():
    try:
        tasks= get_scheduled_tasks()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedule/get_task_result/{task_name}")
async def get_task_result(task_name: str):
    try:
        result = get_task_articles(task_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/schedule/cancel_task/{task_name}")
async def cancel_task(task_name: str):
    try:
        task_result = delete_scheduled_task(task_name)
        return task_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    try:
        task_result = AsyncResult(task_id)
        if task_result.ready():
            return {
                "status": task_result.status,
                "result": task_result.get()
            }
        return {
            "status": task_result.status,
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/all_tasks_id")
async def get_all_tasks_id():
    try:
        i = current_app.control.inspect()
        active = i.active() or {}
        reserved = i.reserved() or {}
        scheduled = i.scheduled() or {}
        task_ids = set()
        for worker_tasks in active.values():
            for task in worker_tasks:
                task_ids.add(task['id'])
        for worker_tasks in reserved.values():
            for task in worker_tasks:
                task_ids.add(task['id'])
        for worker_tasks in scheduled.values():
            for task in worker_tasks:
                task_ids.add(task['request']['id'])
        return list(task_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/task/cancel_task/{task_id}")
async def cancel_task(task_id: str):
    try: 
        task_result = AsyncResult(task_id)
        if task_result.state == 'SUCCESS':
            return {"status": "Task already completed or not found"}
        else:
            task_result.revoke(terminate=True)
            return {"status": "Task cancelled "}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))