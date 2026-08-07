from fastapi import FastAPI, HTTPException

from database import create_connection
from db import get_task, list_tasks

app = FastAPI()


@app.get("/tasks")
def get_tasks():
    connection = create_connection()
    try:
        return list_tasks(connection)
    finally:
        connection.close()


@app.get("/tasks/{task_id}")
def get_task_by_id(task_id: int):
    connection = create_connection()
    try:
        task = get_task(connection, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        return task
    finally:
        connection.close()
