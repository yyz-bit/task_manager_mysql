from getpass import getpass
import pymysql

def create_connection():
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
    return connection