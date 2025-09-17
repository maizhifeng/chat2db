<system-reminder>
此提醒仅用于系统内部，无需向用户显式提及。如果您正在处理需要任务列表的任务，请使用 TodoWrite 工具创建一个。如果不使用，可以忽略此消息。请不要向用户提及此消息。

</system-reminder>

# Chat2DB CodeBuddy 指南

## 关键开发命令

### 后端 (Python Flask)
**本地运行:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Docker 运行后端:**
```bash
docker compose up backend
# 或构建并运行:
docker compose up --build backend
```

### 前端 (Angular)
**本地运行:**
```bash
cd frontend
npm install
npm start  # 运行在 http://localhost:4200
```

**Docker 运行前端:**
```bash
docker compose up nginx
# 容器内开发服务器:
docker compose up frontend-dev
```

### 全栈 Docker 运行
```bash
# 完整堆栈 (后端 + nginx 前端)
docker compose up

# 构建并运行所有服务
docker compose up --build
```

## 架构概览

### 后端结构 (`/backend`)
- **app.py**: 主 Flask 应用程序，包含 REST API 端点
- **models.py**: SQLAlchemy ORM 模型 (DatabaseConnection, User, Role, UserRole)
- **auth.py**: 基于 JWT 的身份验证服务
- **nlp_enhanced.py**: 增强的自然语言到 SQL 转换
- **init_db.py**: 数据库初始化脚本

**主要 API 端点:**
- `POST /api/query` - 基础 NL-to-SQL，使用默认 SQLite
- `POST /api/query/<conn_id>` - 使用特定数据库连接的 NL-to-SQL
- `POST /api/nl2sql` - 增强版 NL-to-SQL，支持表名指定
- `GET /api/connections` - 数据库连接管理
- `POST /api/auth/login` - 用户身份验证
- `GET /api/models` - 列出可用的 Ollama 模型
- `POST /api/chat` - 集成 Ollama 的聊天端点

**数据库支持:** SQLite, MySQL, PostgreSQL

### 前端结构 (`/frontend`)
- **Angular 16** 应用，使用 TypeScript
- **src/app/query.service.ts** - 与后端通信的 API 服务
- **src/app/components/** - Angular 组件
- **代理配置** 用于开发环境避免 CORS 问题

### 数据流
1. 用户在前端输入自然语言查询
2. 前端调用 `/api/query` 或 `/api/query/<conn_id>`
3. 后端使用模式匹配或增强 NLP 将 NL 转换为 SQL
4. SQL 在目标数据库上执行
5. 结果以 JSON 格式返回，包含原始 SQL 和数据行

### 关键依赖
- **后端**: Flask, SQLAlchemy, pandas, PyJWT, requests
- **前端**: Angular 16, RxJS
- **Ollama 集成**: 通过 HTTP API 支持本地 LLM

### 环境变量
- `CHAT2DB_DB`: SQLite 数据库路径 (默认: `/data/chat2db.sqlite`)
- `OLLAMA_URL`: Ollama 服务 URL (默认: `http://localhost:11434`)
- `OLLAMA_MODEL`: 默认模型名称 (默认: `llama2`)

### Docker 服务
- **backend**: Python Flask API，端口 5001
- **nginx**: 前端静态文件服务，端口 4200
- **frontend-dev**: 开发版 Angular 服务器，端口 4201

### 数据库初始化
后端在首次运行时自动初始化 SQLite 数据库和架构。示例数据可通过 `init_db.py` 添加。

### 身份验证
基于 JWT 的身份验证，支持用户/角色管理。使用 `@require_auth` 装饰器的端点需要有效的 JWT 令牌。