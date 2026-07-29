from getpass import getpass

import pymysql


def read_integer(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("请输入整数")


def list_tasks(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, title, is_done FROM tasks ORDER BY id ASC")
        return cursor.fetchall()
    finally:
        cursor.close()


def display_tasks(tasks):
    for task in tasks:
        status = "已完成" if task["is_done"] else "未完成"
        print(f"{task['id']}. [{status}] {task['title']}")


def create_task(connection, user_id, category_id, title, description):
    cursor = connection.cursor()
    try:
        connection.begin()
        cursor.execute(
            "INSERT INTO tasks (user_id, category_id, title, description) "
            "VALUES (%s, %s, %s, %s)",
            (user_id, category_id, title, description),
        )
        new_task_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO task_logs (task_id, action_type, details) "
            "VALUES (%s, %s, %s)",
            (new_task_id, "created", "创建任务"),
        )
        connection.commit()
        print("任务创建成功")
    except pymysql.MySQLError as error:
        connection.rollback()
        print(f"任务创建失败：{error}")

    finally:
        cursor.close()



def complete_task(connection, task_id):
    cursor = connection.cursor()

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
                "INSERT INTO task_logs (task_id, action_type, details) VALUES (%s, %s, %s) ",
                (task_id, "status_changed", "任务状态改为已完成")
            )
            connection.commit()
            print("Task updated and log created")

    except pymysql.MySQLError as error:
        connection.rollback()
        print(f"Database error: {error}")

    finally:
        cursor.close()


def show_menu():
    print("1. 查看任务")
    print("2. 完成任务")
    print("3. 创建任务")
    print("0. 退出")
    return input("请选择操作: ")


def main():
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
    try:
        while True:
            choice = show_menu()

            if choice == "1":
                tasks = list_tasks(connection)
                display_tasks(tasks)

            elif choice == "2":
                task_id = read_integer("Task ID: ")
                complete_task(connection, task_id)

            elif choice == "3":
                user_id = read_integer("User ID: ")
                category_id = read_integer("Category ID: ")
                title = input("Title: ").strip()

                if title:
                    description = input("任务描述（可留空）: ").strip() or None
                    create_task(connection, user_id, category_id, title, description)
                else:
                    print("任务标题不能为空")

            elif choice == "0":
                print("程序已退出：")
                break

            else:
                print("无效选择，请重新输入")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
