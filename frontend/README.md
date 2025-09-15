# Frontend (Angular CLI)

这是一个基于 Angular 的最小前端项目（已迁移为 Angular CLI 风格）。

快速开始：

1. 进入目录

```bash
cd frontend
```

2. 安装依赖

```bash
npm install
```

3. 开发服务器

```bash
npm start
# 或者使用 npx: npx ng serve --open
```

开发服务器默认运行在 http://localhost:4200。

构建生产包：

```bash
npm run build
# 生成目录: dist/chat2db-frontend
```

代理后端（避免 CORS）建议：

创建一个 `proxy.conf.json`（示例）在 `frontend/`：

```json
{
	"/api": {
		"target": "http://localhost:5001",
		"secure": false,
		"changeOrigin": true
	}
}
```

然后用 `ng serve` 时指定代理：

```bash
npx ng serve --proxy-config proxy.conf.json
```

注意：`QueryService` 的 base URL 目前硬编码为 `http://localhost:5001/api`（位于 `src/app/query.service.ts`）。如果使用代理，你可以把 `base` 改为 `/api` 来统一调用方式。

下一步建议：
- 使用 `ng` CLI 初始化完整项目模板（如果想要更严格的约定/测试/CI）。
- 添加单元测试（Karma/Jasmine 或 Jest）和简单的 E2E 测试。

前端说明

该目录包含可复制到 Angular 项目的简单组件和服务示例。

示例文件：
- chat/query.service.ts  -> 与后端通信的 Angular 服务
- chat/query.component.ts/html -> 简单 UI，发送查询并显示结果

使用方法：在你现有的 Angular 项目中创建 `src/app/chat/` 目录并复制这两个文件，然后在模块中声明组件并提供服务。


Docker 构建与运行
------------------

项目已经包含用于生产的 `Dockerfile` 与 `nginx` 配置，并且可以通过 `docker-compose` 直接构建并启动前后端：

默认（镜像内构建）：

```bash
# 在仓库根目录运行
docker-compose up --build
```

预构建（CI/本地先构建 dist，再构建镜像）：

```bash
cd frontend
npm ci
npm run build -- --configuration production
# 然后回到仓库根，使用 prebuilt target 构建镜像
FRONTEND_BUILD_TARGET=prebuilt docker-compose build frontend
docker-compose up -d
```

API 代理说明
-------------

为避免浏览器跨域，生产镜像的 Nginx 已配置把 `/api/` 路径代理到容器内的 `backend:5001`。因此在生产构建时前端会使用相对路径 `'/api'`（见 `src/environments/environment.prod.ts`）。

开发模式建议：在本地使用 `ng serve` 时可以启用代理（proxy.conf.json），或在 `environment.ts` 中保留 `apiBase='http://localhost:5001/api'`。

验证
----

1. 启动后在浏览器打开 http://localhost:4200
2. 在前端 UI 提交一个自然语言查询，前端会通过 `/api/query` 调用后端并显示返回的 SQL 与数据。

模型选择说明
---------------

前端 UI 现在支持从后端列出可用的大模型并选择一个模型发送请求（如果后端可访问本地 Ollama 服务）。

- 点击“刷新模型”会调用后端的 `/api/models`，后端会代理到 `OLLAMA_URL`（默认为 `http://localhost:11434`）。
- 选择模型并点击“加载并发送”会把当前输入作为消息发送到 `/api/chat`，并带上所选模型名称。
- 如果后端无法访问 Ollama，模型列表会为空，且 `/api/chat` 将返回错误信息。请参阅 `../backend/README_OLLAMA.md` 了解如何启动 Ollama。
