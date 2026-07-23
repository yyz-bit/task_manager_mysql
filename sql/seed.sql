SET NAMES utf8mb4;

USE task_manager_mysql;

INSERT INTO users (username)
	VALUES
	('zhangsan'),
	('lisi');

INSERT INTO categories (name)
	VALUES
	('Python'),
	('MySQL'),
	('Linux');

INSERT INTO tasks (user_id, category_id, title, description, is_done)
	VALUES
	(1, 2, '完成数据库初始化脚本',  '创建四张核心表', 1),
	(1, 1, '编写PyMySQL数据访问层', NULL, 0),
	(2, 3, '练习Linux日志排查', '查看服务运行日志', 0),
	(2, 2, '验证事务回滚', NULL, 0);

INSERT INTO task_logs (task_id, action_type, details)
	VALUES
	(1, 'created', '创建任务'),
	(1, 'status_changed', '任务状态改为已完成'),
	(2, 'created', '创建任务'),
	(3, 'created', '创建任务'),
	(4, 'created', '创建任务');
