# task_manager_mysql

使用 Python 和 MySQL 构建的命令行任务管理器。项目通过 PyMySQL 访问数据库，并使用事务保证任务数据和操作日志同时成功或同时回滚。

## 功能

- 查看任务及其所属用户、分类和完成状态
- 创建任务并记录创建日志
- 修改任务并记录修改日志
- 完成任务并防止重复写入状态日志
- 按完成状态筛选任务
- 按标题关键词搜索任务
- 查看任务的操作日志
- 软删除任务并保留历史日志

## 技术栈

- Python 3
- MySQL 8.4
- PyMySQL
- python-dotenv

## 项目结构

```text
task_manager_mysql/
|-- db.py                  # 菜单、输入输出和任务业务逻辑
|-- database.py            # 数据库配置与连接创建
|-- requirements.txt       # Python 依赖
|-- .env.example           # 环境变量示例，不包含真实密码
|-- sql/
|   |-- schema.sql         # 创建数据库和数据表
|   |-- seed.sql           # 写入初始用户、分类、任务和日志
|   `-- transaction_demo.sql
`-- README.md
```

## 安装与运行

### 1. 创建并激活虚拟环境

在项目根目录的 PowerShell 中执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
python -m pip install -r .\requirements.txt
```

### 3. 初始化数据库

使用 MySQL `root` 账号登录 MySQL 8.4 Command Line Client，然后依次加载建表和初始数据脚本：

```sql
SOURCE C:/path/to/task_manager_mysql/sql/schema.sql;
SOURCE C:/path/to/task_manager_mysql/sql/seed.sql;
```

`schema.sql` 必须先于 `seed.sql` 执行。请将示例路径替换为项目在本机的实际绝对路径。

### 4. 创建应用账号

继续使用 MySQL `root` 账号执行：

```sql
CREATE USER 'task_app'@'localhost'
IDENTIFIED BY 'replace_with_strong_password';

GRANT SELECT, INSERT, UPDATE
ON task_manager_mysql.*
TO 'task_app'@'localhost';

SHOW GRANTS FOR 'task_app'@'localhost';
```

`root` 只负责初始化和授权。程序日常运行使用权限更小的 `task_app`；软删除通过 `UPDATE` 实现，因此不需要授予 `DELETE` 权限。

### 5. 配置环境变量

在项目根目录复制环境变量示例：

```powershell
Copy-Item .\.env.example .\.env
```

编辑新生成的 `.env`：

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=task_app
DB_PASSWORD=创建 task_app 时设置的密码
DB_NAME=task_manager_mysql
```

`.env` 已被 Git 忽略，不要把真实数据库密码写入 `.env.example` 或提交到仓库。

### 6. 启动程序

```powershell
python .\db.py
```

程序启动后，可通过编号菜单查看、创建、修改、完成、搜索和删除任务，也可以查看每个任务的操作日志。

## 数据一致性

创建、修改、完成和删除任务时，业务数据与对应日志位于同一个事务中：全部成功时提交，任何一步失败时回滚。任务删除采用 `is_deleted` 标记实现，普通查询会隐藏已删除任务，但历史日志仍然保留。
