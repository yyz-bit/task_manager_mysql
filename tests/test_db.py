from db import display_tasks
from db import display_task_logs


def test_display_tasks_shows_completed_task(capsys):
    tasks = [
        {
            "id": 100,
            "title": "完成测试任务",
            "is_done": 1,
            "username": "lisi",
            "category_name": "MySQL",
        }

    ]

    display_tasks(tasks)

    captured = capsys.readouterr()

    assert captured.out == (
        "100. [已完成] 完成测试任务 | 用户：lisi | 分类：MySQL\n"

    )


def test_display_tasks_shows_unfinished_task(capsys):
    tasks = [
        {
            "id": 99,
            "title": "测试任务",
            "is_done": 0,
            "username": "zhangsan",
            "category_name": "Python",
        }
    ]
    display_tasks(tasks)
    captured = capsys.readouterr()
    assert captured.out == (
        "99. [未完成] 测试任务 | 用户：zhangsan | 分类：Python\n"
    )


def test_display_task_logs(capsys):
    logs = [
        {
            "id": 12,
            "action_type": "created",
            "details": "创建任务",
            "created_at": "2026-08-03 20:02:46",
        },
        {
            "id": 13,
            "action_type": "updated",
            "details": "修改任务信息",
            "created_at": "2026-08-03 20:04:58",
        }
    ]
    display_task_logs(logs)
    captured = capsys.readouterr()
    assert captured.out == (
        "12. [created] 创建任务 | 时间：2026-08-03 20:02:46\n"
        "13. [updated] 修改任务信息 | 时间：2026-08-03 20:04:58\n"
    )
