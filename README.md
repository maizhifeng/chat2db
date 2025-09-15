# chat2db

本项目是一个简化版的 Chat2DB 原型：

目录结构：


运行说明见各目录下 README。
# chat2db

本项目是一个简化版的 Chat2DB 原型：
- 前端：Angular 项目模板（示例组件和服务）
- 后端：Python Flask API，提供自然语言 -> SQL 的简单转换，并在本地 SQLite 上执行查询

目录结构：

- `backend/`  -> Flask 后端代码
- `frontend/` -> Angular 前端示例（只包含可复制粘贴的组件和服务）

运行说明见各目录下 README。下面包含 Docker 化的快速使用说明。

## 使用 Docker（快速开始）

本仓库包含 `docker-compose.yml`，可以用来在容器中运行后端并挂载持久化的 SQLite 数据库。

示例步骤：

1. 构建并启动服务：

```bash
cd /home/mzf/chat2db
docker compose up --build -d
```

2. 第一次启动后会在 `./data/chat2db.sqlite` 下生成示例数据库（由容器内部的初始化脚本写入）。

3. 测试后端接口（在宿主机运行）：

```bash
curl -X POST http://127.0.0.1:5001/api/query -H "Content-Type: application/json" -d '{"query":"show me employees"}'
```

4. 停止并移除容器：

```bash
docker compose down
```

注意：如果你正在使用较旧的 Docker / Compose，请使用 `docker-compose` 而不是 `docker compose`。

前端部分示例文件位于 `frontend/`，你可以将其复制到你的 Angular 项目并通过 `QueryService` 调用后端。
