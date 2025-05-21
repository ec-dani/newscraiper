import asyncio
from typing import Dict
from crawl4ai import AsyncWebCrawler
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
from celery import current_app

from celery_task import crawl_task


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
    return {"message": "Bienvenido a News Analyzer API"}



@app.get("/crawl_async_with")
async def crawl_aw(url):
    try:
        task = crawl_task.delay(url)
        
        return {
            "task_id": task.id,
            "status": "pending"
        }
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

@app.get("/all_tasks_id")
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
    
@app.get("/cancel_task/{task_id}")
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