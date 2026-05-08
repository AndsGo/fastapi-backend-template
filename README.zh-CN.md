# FastAPI 后端模板

这是一个可复用的纯后端 FastAPI 项目模板，适合用作模块化单体服务的基础工程。

[English README](README.md)

## 环境要求

- Python 3.11 或更高版本。
- 使用持久化能力时需要 PostgreSQL 或 MySQL。
- 使用分布式定时任务或 Redis 缓存能力时需要 Redis。

## 项目包含什么

- FastAPI API 版本管理和依赖注入。
- SQLAlchemy 模型、仓储、会话管理和 Alembic 数据库迁移。
- 通过 `DATABASE_URL` 支持 PostgreSQL 和 MySQL。
- Redis 客户端和统一的 Redis key 模板。
- 定时任务定义、调度器、并发 worker 和任务注册表。
- 输出到 stdout 的 JSON 日志，以及可选的本地滚动日志文件。
- 清晰的 API、service、repository、model、schema 分层。
- 一个 `examples` 示例模块，用于展示推荐的代码组织方式。

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

编辑 `.env`，至少确认 `DATABASE_URL` 指向你的数据库。Redis 是可选的，
除非你要运行分布式任务或使用 Redis 缓存能力。

关键环境变量：

- `APP_ENV`：运行环境，例如 `local`、`staging`、`production`。
- `DATABASE_URL`：SQLAlchemy 数据库连接地址，支持 PostgreSQL 和 MySQL。
- `SECRET_KEY`：安全相关辅助函数使用的应用密钥，不能使用示例值。
- `BACKEND_CORS_ORIGINS`：允许访问 API 的浏览器来源，格式为 JSON 数组。
- `REDIS_URL`：Redis 连接地址。
- `REDIS_PREFIX`：当前应用使用的 Redis key 前缀。

## 数据库迁移

应用已有迁移：

```bash
alembic upgrade head
```

修改模型后生成新的迁移：

```bash
alembic revision --autogenerate -m "describe change"
```

## 运行 API

```bash
uvicorn app.main:app --reload
```

启动后打开：

```text
http://127.0.0.1:8000/docs
```

## 运行定时任务

启动调度器：

```bash
python -m app.jobs.runner scheduler --interval-seconds 10
```

启动 worker：

```bash
python -m app.jobs.runner worker --interval-seconds 5 --worker-id worker-1 --max-workers 4
```

也可以使用安装后的命令行入口：

```bash
backend-jobs worker --once --max-workers 4
```

## 验证项目

```bash
python -m pytest
python -m ruff check .
lint-imports
python -m mypy app
```

GitHub Actions 会在推送到 `main` 和针对 `main` 的 pull request 中运行同样的验证命令。

## 作为模板使用

新增业务模块时，建议参考现有的 `examples` 模块：

- 在 `app/models` 中新增数据库模型。
- 在 `app/schemas` 中新增请求和响应 schema。
- 在 `app/repositories` 中封装数据库访问。
- 在 `app/services` 或 `app/application` 中编写业务逻辑。
- 在 `app/api/v1/endpoints` 中暴露 HTTP 接口，并注册到 v1 router。
- 在 `tests` 中补充 repository、service、application use case 和 endpoint 测试。
- 根据变更同步更新 `docs` 下的相关文档。

接口层应保持轻量，业务行为放在 service 或 application 层，数据库查询放在 repository 层。

## 认证和权限

当前项目只保留认证和权限的占位设计。正式用于生产项目前，需要先确认目标方案，
例如 SSO、OAuth2、JWT、RBAC 或其他组织内统一认证体系。

## 主要文档

- [架构说明](docs/architecture.md)
- [开发指南](docs/development-guide.md)
- [数据库设计](docs/database-design.md)
- [任务系统指南](docs/job-guide.md)
- [项目框架规范](docs/project-framework-standards.md)
- [认证与安全占位说明](docs/security-and-auth-placeholder.md)
