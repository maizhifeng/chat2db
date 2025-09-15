# Frontend

This folder contains a minimal Angular-based frontend for Chat2DB.

Installation:

1. cd frontend
2. npm install
3. npm start

The dev server runs on http://localhost:4200 by default and proxies API calls to the backend running on :5001.
前端说明

该目录包含可复制到 Angular 项目的简单组件和服务示例。

示例文件：
- chat/query.service.ts  -> 与后端通信的 Angular 服务
- chat/query.component.ts/html -> 简单 UI，发送查询并显示结果

使用方法：在你现有的 Angular 项目中创建 `src/app/chat/` 目录并复制这两个文件，然后在模块中声明组件并提供服务。
