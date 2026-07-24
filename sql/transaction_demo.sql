USE task_manager_mysql;

START TRANSACTION;

UPDATE tasks
SET is_done = 1
WHERE id = 4;

INSERT INTO task_logs (task_id, action_type, details)
VALUES
(4, 'status_changed', '任务状态改为已完成');

COMMIT;

