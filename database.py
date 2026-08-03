import os
from getpass import getpass

import pymysql
from dotenv import load_dotenv

load_dotenv()


def create_connection():
    mysql_password = os.getenv("DB_PASSWORD") or getpass("MySQL password: ")
    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "task_app"),
        password=mysql_password,
        database=os.getenv("DB_NAME", "task_manager_mysql"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection
