import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import create_connection
from db import get_task, list_tasks, create_task


class TaskCreate(BaseModel):
    user_id: int
    category_id: int
    title: str
    description: str | None = None


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


@app.post("/tasks", status_code=201)
def create_task_endpoint(task: TaskCreate):
    connection = create_connection()
    try:
        new_task_id = create_task(
            connection,
            task.user_id,
            task.category_id,
            task.title,
            task.description,
        )
        return {"id": new_task_id}
    except pymysql.IntegrityError as error:
        raise HTTPException(
            status_code=400,
            detail="用户或分类不存在",
        ) from error
    except pymysql.MySQLError as error:
        raise HTTPException(
            status_code=500,
            detail="创建任务失败",
        ) from error
    finally:
        connection.close()
