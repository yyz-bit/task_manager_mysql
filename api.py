from fastapi import FastAPI

from database import create_connection
from db import list_tasks

app = FastAPI()


@app.get("/tasks")
def get_tasks():
    connection = create_connection()
    try:
        return list_tasks(connection)
    finally:
        connection.close()
