from db import display_tasks


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
