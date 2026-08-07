import pymysql
from database import create_connection


# 输入处理
def read_integer(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("请输入整数")


# 只读查询：每个函数独立管理游标，数据库连接由 main() 统一管理。
def list_categories(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        return cursor.fetchall()
    finally:
        cursor.close()


def list_tasks(connection):
    cursor = connection.cursor()
    try:
        # JOIN 后一次取得任务、用户和分类信息。
        cursor.execute(
            "SELECT tasks.id, tasks.title, tasks.is_done, users.username, categories.name AS category_name FROM tasks "
            "INNER JOIN users ON tasks.user_id = users.id "
            "INNER JOIN categories ON  tasks.category_id = categories.id "
            "WHERE tasks.is_deleted = 0 "
            "ORDER BY tasks.id ASC")
        return cursor.fetchall()
    finally:
        cursor.close()


def get_task(connection, task_id):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT tasks.id, tasks.title, tasks.is_done, users.username, "
            "categories.name AS category_name "
            "FROM tasks "
            "INNER JOIN users ON tasks.user_id = users.id "
            "INNER JOIN categories ON tasks.category_id = categories.id "
            "WHERE tasks.id = %s AND tasks.is_deleted = 0",
            (task_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def list_tasks_by_status(connection, status):
    cursor = connection.cursor()
    try:
        # SQL 和参数分开传入，避免手工拼接用户输入。
        cursor.execute(
            "SELECT tasks.id, tasks.title, tasks.is_done, users.username, categories.name AS category_name FROM tasks "
            "INNER JOIN users ON tasks.user_id = users.id "
            "INNER JOIN categories ON  tasks.category_id = categories.id "
            "WHERE tasks.is_done = %s AND tasks.is_deleted = 0 "
            "ORDER BY tasks.id ASC",
            (status,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def list_task_logs(connection, task_id):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT id, action_type, details, created_at "
            "FROM task_logs "
            "WHERE task_id = %s "
            "ORDER BY id ASC ",
            (task_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def search_tasks(connection, keyword):
    cursor = connection.cursor()
    # 两侧的 % 表示关键词可以出现在标题任意位置。
    pattern = f"%{keyword}%"
    try:
        cursor.execute(
            "SELECT tasks.id, tasks.title, tasks.is_done, users.username, categories.name AS category_name FROM tasks "
            "INNER JOIN users ON tasks.user_id = users.id "
            "INNER JOIN categories ON  tasks.category_id = categories.id "
            "WHERE tasks.title LIKE %s AND tasks.is_deleted = 0 "
            "ORDER BY tasks.id ASC",
            (pattern,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def list_users(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, username FROM users ORDER BY id ASC")
        return cursor.fetchall()
    finally:
        cursor.close()


# 结果展示：这些函数只格式化已查到的数据，不访问数据库。
def display_users(users):
    print("可选用户：")
    for user in users:
        print(f"{user['id']}. {user['username']}")


def display_tasks(tasks):
    for task in tasks:
        status = "已完成" if task["is_done"] else "未完成"
        print(f"{task['id']}. [{status}] {task['title']} | "
              f"用户：{task['username']} | 分类：{task['category_name']}")


def display_task_logs(logs):
    for log in logs:
        print(f"{log['id']}. [{log['action_type']}] {log['details']} | 时间：{log['created_at']}")


def display_categories(categories):
    print("可选分类：")
    for category in categories:
        print(f"{category['id']}. {category['name']}")


# 写操作：业务数据与对应日志放在同一事务中，避免只成功一半。
def create_task(connection, user_id, category_id, title, description):
    cursor = connection.cursor()
    try:
        connection.begin()
        cursor.execute(
            "INSERT INTO tasks (user_id, category_id, title, description) "
            "VALUES (%s, %s, %s, %s)",
            (user_id, category_id, title, description),
        )
        # 保存新任务的自增 ID，供日志表建立关联。
        new_task_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO task_logs (task_id, action_type, details) "
            "VALUES (%s, %s, %s)",
            (new_task_id, "created", "创建任务"),
        )
        connection.commit()
        return new_task_id

    except pymysql.MySQLError:
        connection.rollback()
        raise
    finally:
        cursor.close()


def update_task(connection, task_id, title, description):
    cursor = connection.cursor()
    try:
        connection.begin()
        # 先确认任务存在，才能区分“不存在”和“内容没有变化”。
        cursor.execute(
            "SELECT id FROM tasks WHERE id = %s AND is_deleted = 0",
            (task_id,),
        )
        task = cursor.fetchone()
        if task is None:
            connection.rollback()
            print("任务不存在")
            return
        cursor.execute(
            "UPDATE tasks SET title = %s, description = %s WHERE id = %s AND is_deleted = 0",
            (title, description, task_id),
        )
        update_rows = cursor.rowcount
        if update_rows == 0:
            connection.rollback()
            print("任务内容没有变化")
            return
        cursor.execute(
            "INSERT INTO task_logs (task_id, action_type, details) "
            "VALUES (%s, %s, %s)",
            (task_id, "updated", "修改任务信息"),
        )
        connection.commit()
        print("任务更新成功")
    except pymysql.MySQLError as error:
        connection.rollback()
        print(f"任务更新失败：{error}")

    finally:
        cursor.close()


def delete_task(connection, task_id):
    cursor = connection.cursor()
    try:
        connection.begin()
        cursor.execute(
            "UPDATE tasks SET is_deleted = 1 "
            "WHERE id = %s AND is_deleted = 0",
            (task_id,),
        )
        deleted_rows = cursor.rowcount
        if deleted_rows == 0:
            connection.rollback()
            return False
        else:
            cursor.execute(
                "INSERT INTO task_logs (task_id, action_type, details) VALUES (%s, %s, %s)",
                (task_id, "deleted", "删除任务"),
            )
            connection.commit()
            return True
    except pymysql.MySQLError:
        connection.rollback()
        raise
    finally:
        cursor.close()


def complete_task(connection, task_id):
    cursor = connection.cursor()

    try:

        connection.begin()
        # 只允许未完成任务从 0 变为 1，避免重复写入完成日志。
        cursor.execute(
            "UPDATE tasks SET is_done = %s "
            "WHERE id = %s AND is_done = %s AND is_deleted = 0",
            (1, task_id, 0)
        )
        updated_rows = cursor.rowcount

        if updated_rows == 0:
            connection.rollback()
            return False
        else:
            cursor.execute(
                "INSERT INTO task_logs (task_id, action_type, details) VALUES (%s, %s, %s) ",
                (task_id, "status_changed", "任务状态改为已完成")
            )
            connection.commit()
            return True


    except pymysql.MySQLError:
        connection.rollback()
        raise

    finally:
        cursor.close()


# 菜单与程序入口
def show_menu():
    print("1. 查看任务")
    print("2. 完成任务")
    print("3. 创建任务")
    print("4. 按状态查看任务")
    print("5. 按标题搜索任务")
    print("6. 查看任务日志")
    print("7. 修改任务")
    print("8. 删除任务")
    print("0. 退出")
    return input("请选择操作: ")


def main():
    connection = create_connection()
    try:
        while True:
            choice = show_menu()

            if choice == "1":
                tasks = list_tasks(connection)
                display_tasks(tasks)

            elif choice == "2":
                task_id = read_integer("Task ID: ")
                try:
                    complete = complete_task(connection, task_id)

                    if complete:
                        print("任务已完成")
                    else:
                        print("任务不存在、已完成或已删除")
                except pymysql.MySQLError as error:
                    print(f"任务完成失败：{error}")

            elif choice == "3":
                users = list_users(connection)
                display_users(users)
                user_id = read_integer("User ID: ")

                categories = list_categories(connection)
                display_categories(categories)
                category_id = read_integer("Category ID: ")

                title = input("Title: ").strip()

                if title:
                    description = input("任务描述（可留空）: ").strip() or None
                    try:
                        new_task_id = create_task(
                            connection,
                            user_id,
                            category_id,
                            title,
                            description,
                        )
                        print(f"任务创建成功，ID: {new_task_id}")
                    except pymysql.MySQLError as error:
                        print(f"任务创建失败：{error}")
                else:
                    print("任务标题不能为空")

            elif choice == "4":
                status = read_integer("任务状态（0-未完成，1-已完成）： ")
                if status in (0, 1):
                    tasks = list_tasks_by_status(connection, status)
                    display_tasks(tasks)
                else:
                    print("状态只能是0 或 1")

            elif choice == "5":
                keyword = input("请输入关键字：").strip()
                if keyword:
                    tasks = search_tasks(connection, keyword)
                    if tasks:
                        display_tasks(tasks)
                    else:
                        print("未找到匹配任务")
                else:
                    print("关键词不能为空！")

            elif choice == "6":
                task_id = read_integer("Task ID: ")
                logs = list_task_logs(connection, task_id)

                if logs:
                    display_task_logs(logs)
                else:
                    print("未找到该任务的日志")

            elif choice == "7":
                tasks = list_tasks(connection)
                display_tasks(tasks)

                task_id = read_integer("Task ID: ")
                title = input("New Title: ").strip()
                if title:
                    description = input("任务描述（可留空）: ").strip() or None
                    update_task(connection, task_id, title, description)
                else:
                    print("任务新标题不能为空")

            elif choice == "8":
                tasks = list_tasks(connection)
                display_tasks(tasks)

                task_id = read_integer("Task ID: ")
                confirm = input("确定要删除该任务吗？(y/n): ").strip().lower()

                if confirm == "y":
                    try:
                        deleted = delete_task(connection, task_id)
                        if deleted:
                            print("任务删除成功")
                        else:
                            print("任务不存在或已删除")
                    except pymysql.MySQLError as error:
                        print(f"任务删除失败：{error}")
                else:
                    print("已取消删除")


            elif choice == "0":
                print("程序已退出：")
                break

            else:
                print("无效选择，请重新输入")

    finally:
        connection.close()


# 被其他模块导入时不自动启动交互程序。
if __name__ == "__main__":
    main()
