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
