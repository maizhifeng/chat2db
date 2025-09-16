# Chat2DB 功能扩展设计文档

## 1. 概述

### 1.1 项目背景
当前项目是一个简化版的 Chat2DB 原型，旨在通过自然语言处理将用户输入的自然语言转换为 SQL 查询，并在数据库上执行。目前功能较为基础，仅支持简单的自然语言到 SQL 的转换。

### 1.2 目标
参考完整版 Chat2DB 的功能特性，对当前原型进行功能扩展，提升其功能完整性和用户体验，使其更接近生产可用的数据库管理工具。

### 1.3 核心功能扩展方向
- 数据库连接管理
- 多数据库支持
- 增强的自然语言处理能力
- 数据表管理功能
- 可视化报表功能
- 用户认证和权限管理

## 2. 架构设计

### 2.1 当前架构
```
┌─────────────────┐    HTTP    ┌──────────────────┐
│   Angular 前端   │ ──────────▶ │  Flask 后端服务   │
└─────────────────┘            └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │   SQLite 数据库   │
                                └──────────────────┘
```

### 2.2 扩展后架构
```
┌─────────────────┐    HTTP    ┌──────────────────┐
│   Angular 前端   │ ──────────▶ │  Flask 后端服务   │
└─────────────────┘            └──────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
         ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
         │  MySQL/PostgreSQL │  │   CSV 文件数据源  │  │ 其他数据库(未来)  │
         └──────────────────┘  └──────────────────┘  └──────────────────┘
```

## 3. 功能模块设计

### 3.1 数据库连接管理模块

#### 3.1.1 功能描述
允许用户创建、编辑、删除和测试数据库连接，支持多种数据库类型。

#### 3.1.2 数据模型
```python
class DatabaseConnection:
    id: str
    name: str
    type: str  # mysql, postgresql, sqlite, sqlserver, oracle等
    host: str
    port: int
    username: str
    password: str
    database: str
    environment: str  # dev, test, prod
```

#### 3.1.3 API 接口
- `POST /api/connections` - 创建数据库连接
- `GET /api/connections` - 获取所有数据库连接
- `GET /api/connections/{id}` - 获取指定数据库连接
- `PUT /api/connections/{id}` - 更新数据库连接
- `DELETE /api/connections/{id}` - 删除数据库连接
- `POST /api/connections/{id}/test` - 测试数据库连接

### 3.2 多数据库支持模块

#### 3.2.1 功能描述
扩展当前仅支持 SQLite 的限制，支持多种主流数据库。

#### 3.2.2 支持的数据库类型
- MySQL
- PostgreSQL
- CSV文件（作为数据源）

#### 3.2.3 实现方案
使用 SQLAlchemy 作为 ORM 层，通过数据库连接配置动态创建引擎。

对于CSV文件支持：
1. 提供文件上传接口
2. 解析CSV文件并将其数据加载到内存或临时数据库表中
3. 提供类似数据库表的查询接口

### 3.3 增强的自然语言处理模块

#### 3.3.1 功能描述
提升自然语言到 SQL 的转换准确性和复杂度支持。

#### 3.3.2 实现方案
1. 集成更强大的大语言模型（如 Chat2DB-SQL-7B）
2. 增加上下文理解能力
3. 支持复杂查询（JOIN、子查询等）

#### 3.3.3 API 接口
- `POST /api/nl2sql` - 自然语言转 SQL
- `POST /api/sql2nl` - SQL 转自然语言

### 3.4 数据表管理模块

#### 3.4.1 功能描述
提供数据表的增删改查功能，支持 AI 辅助建表。

#### 3.4.2 功能列表
- 表结构查看
- 表数据浏览
- 表结构修改
- AI 辅助建表

#### 3.4.3 API 接口
- `GET /api/connections/{id}/tables` - 获取所有表
- `GET /api/connections/{id}/tables/{name}` - 获取表结构
- `POST /api/connections/{id}/tables` - 创建表
- `PUT /api/connections/{id}/tables/{name}` - 修改表结构
- `DELETE /api/connections/{id}/tables/{name}` - 删除表

### 3.5 可视化报表模块

#### 3.5.1 功能描述
支持数据可视化展示，提供图表生成和看板功能。

#### 3.5.2 功能列表
- 数据图表生成
- 看板管理
- AI 辅助生成报表

#### 3.5.3 数据模型
```python
class Dashboard:
    id: str
    name: str
    description: str
    created_at: datetime

class Chart:
    id: str
    dashboard_id: str
    name: str
    type: str  # bar, line, pie 等
    query: str
    config: dict
```

### 3.6 用户认证和权限管理模块

#### 3.6.1 功能描述
增加用户认证和权限管理功能，确保数据安全。

#### 3.6.2 功能列表
- 用户注册/登录
- 角色权限管理
- 连接权限控制

#### 3.6.3 数据模型
```python
class User:
    id: str
    username: str
    email: str
    password_hash: str
    created_at: datetime

class Role:
    id: str
    name: str
    permissions: list

class UserRole:
    user_id: str
    role_id: str
```

## 4. 前端组件架构

### 4.1 组件结构
```
app/
├── components/
│   ├── connection-manager/     # 数据库连接管理组件
│   ├── query-editor/           # 查询编辑器组件
│   ├── table-manager/          # 表管理组件
│   ├── dashboard/              # 报表看板组件
│   └── auth/                   # 认证组件
├── services/
│   ├── connection.service.ts
│   ├── query.service.ts
│   ├── table.service.ts
│   ├── dashboard.service.ts
│   └── auth.service.ts
└── models/
    ├── connection.model.ts
    ├── table.model.ts
    ├── chart.model.ts
    └── user.model.ts
```

### 4.2 主要组件说明

#### 4.2.1 ConnectionManagerComponent
- 数据库连接列表展示
- 连接创建/编辑表单
- 连接测试功能

#### 4.2.2 QueryEditorComponent
- SQL 编辑器
- 自然语言输入框
- 查询结果展示

#### 4.2.3 TableManagerComponent
- 表结构展示
- 数据浏览
- 表结构编辑

#### 4.2.4 DashboardComponent
- 看板列表
- 图表展示区域
- 图表配置面板

## 5. 技术实现方案

### 5.1 后端技术栈扩展
- Flask → FastAPI（更好的异步支持和 API 文档）
- SQLAlchemy（ORM 支持多数据库）
- PyJWT（用户认证）
- Celery（异步任务处理）

### 5.2 前端技术栈扩展
- Angular Material（UI 组件库）
- Chart.js（数据可视化）
- Monaco Editor（SQL 编辑器）

### 5.3 数据库设计
```
用户表(users)           连接表(connections)       表结构表(tables)
+-------------+        +-----------------+       +--------------+
| id          |<-------| user_id         |       | id           |
| username    |        | id              |<------| connection_id|
| email       |        | name            |       | name         |
| password    |        | type            |       | schema       |
| created_at  |        | host            |       | created_at   |
+-------------+        | port            |       +--------------+
                       | username        |
                       | password        |
                       | database        |
                       | environment     |
                       | file_path       |  <- 用于CSV文件路径
                       +-----------------+
```

## 6. 部署架构优化

### 6.1 当前部署架构
- 单容器部署
- SQLite 本地存储

### 6.2 优化后部署架构
```
┌─────────────────────────────────────────────────────────────┐
│                    负载均衡器 (Nginx)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Web Server  │   │ Web Server  │   │ Web Server  │
│ (Angular)   │   │ (Angular)   │   │ (Angular)   │
└─────────────┘   └─────────────┘   └─────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
              ┌─────────────────────┐
              │   API Server        │
              │   (FastAPI)         │
              └─────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  MySQL      │   │ PostgreSQL  │   │ SQL Server  │
└─────────────┘   └─────────────┘   └─────────────┘
```

## 7. 安全性设计

### 7.1 认证授权
- JWT Token 认证
- RBAC 权限控制
- 连接信息加密存储

### 7.2 数据安全
- 敏感信息加密传输（HTTPS）
- SQL 注入防护
- 数据访问日志记录

### 7.3 网络安全
- CORS 策略配置
- 请求频率限制
- 输入验证和过滤

## 8. 性能优化方案

### 8.1 查询优化
- SQL 查询缓存
- 数据库连接池
- 分页查询支持

### 8.2 前端优化
- 虚拟滚动（大数据展示）
- 组件懒加载
- HTTP 请求缓存

### 8.3 部署优化
- Docker 容器化部署
- Redis 缓存支持
- CDN 静态资源加速

## 9. 测试策略

### 9.1 单元测试
- 后端 API 测试
- 前端组件测试
- 数据库操作测试

### 9.2 集成测试
- 数据库连接测试
- 认证流程测试
- 端到端功能测试

### 9.3 性能测试
- 并发查询测试
- 大数据集查询测试
- 响应时间监控

## 10. 项目实施计划

### 10.1 阶段一：核心功能扩展（2周）
- 数据库连接管理模块
- 多数据库支持
- 基础用户认证

### 10.2 阶段二：增强功能开发（3周）
- 表管理功能
- 增强的自然语言处理
- 基础可视化报表

### 10.3 阶段三：完善和优化（2周）
- 权限管理
- 性能优化
- 安全加固
- 测试完善

### 10.4 阶段四：文档和部署（1周）
- 用户文档编写
- 部署方案完善
- 使用示例提供




















































