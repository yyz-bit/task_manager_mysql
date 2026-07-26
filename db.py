
from getpass import getpass


import pymysql


mysql_password = getpass("MySQL password: ")

connection = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=mysql_password,
    database="task_manager_mysql",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

cursor = connection.cursor()
target_status = 0
cursor.execute(
    "SELECT id, title, is_done FROM tasks WHERE is_done = %s ORDER BY id ASC ",
    (target_status,),
)
tasks = cursor.fetchall()
for task in tasks:
    print(task)

cursor.close()
connection.close()
