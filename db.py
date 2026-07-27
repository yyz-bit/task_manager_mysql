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
task_id = 2
try:
    connection.begin()
    cursor.execute(
        "UPDATE tasks SET is_done = %s WHERE id = %s AND is_done = %s",
        (1, task_id, 0)
    )
    updated_rows = cursor.rowcount

    if updated_rows == 0:
        connection.rollback()
        print("Task does not exist or is already completed")
    else:
        cursor.execute(
            "INSERT INTO task_logs (task_id, action_type, details) VALUES (%s, %s, %s)",
            (task_id, "status_changed", "任务状态改为已完成")
        )
        connection.commit()
        print("Task updated and log created")

except pymysql.MySQLError as error:
    connection.rollback()
    print(f"Database error: {error}")

finally:
    cursor.close()
    connection.close()
