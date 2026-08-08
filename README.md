# task_manager_mysql

使用 Python、FastAPI 和 MySQL 构建的任务管理项目，同时提供命令行界面和 REST API。项目通过 PyMySQL 访问数据库，使用事务保证任务数据和操作日志同时提交或回滚，并使用 pytest 验证核心功能和 API 数据校验。

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
- FastAPI
- Uvicorn
- Pydantic
- MySQL 8.4
- PyMySQL
- pytest
- python-dotenv

## 项目结构

```text
task_manager_mysql/
|-- api.py                  # FastAPI 应用和接口
|-- db.py                   # 数据访问、业务逻辑和命令行程序
|-- database.py             # 数据库配置与连接创建
|-- requirements.txt        # Python 依赖
|-- .env.example            # 环境变量示例，不包含真实密码
|-- sql/
|   |-- schema.sql          # 创建数据库和数据表
|   |-- seed.sql            # 写入初始数据
|   `-- transaction_demo.sql
|-- tests/
|   |-- test_api.py         # FastAPI 接口测试
|   `-- test_db.py          # 命令行输出和输入测试
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

### 6. 启动命令行程序

```powershell
python .\db.py
```

程序启动后，可通过编号菜单查看、创建、修改、完成、搜索和删除任务，也可以查看每个任务的操作日志。

### 7. 启动 FastAPI 服务

```powershell
python -m uvicorn api:app --reload
```

服务启动后，可访问：

- Swagger 接口文档：http://127.0.0.1:8000/docs
- OpenAPI 描述文件：http://127.0.0.1:8000/openapi.json

### 8. 运行自动化测试

```powershell
python -m pytest -v
```

测试使用 pytest 和 FastAPI TestClient，不需要提前启动 Uvicorn。

## API 接口

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/tasks` | 查询任务列表 |
| GET | `/tasks/{task_id}` | 按 ID 查询任务 |
| POST | `/tasks` | 创建任务 |
| PUT | `/tasks/{task_id}` | 修改任务标题和描述 |
| PATCH | `/tasks/{task_id}/complete` | 将任务标记为已完成 |
| DELETE | `/tasks/{task_id}` | 软删除任务 |

## 数据一致性

创建、修改、完成和删除任务时，业务数据与对应日志位于同一个事务中：全部成功时提交，任何一步失败时回滚。任务删除采用 `is_deleted` 标记实现，普通查询会隐藏已删除任务，但历史日志仍然保留。
