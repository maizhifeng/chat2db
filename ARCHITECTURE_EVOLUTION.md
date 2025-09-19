# Chat2DB 架构演进文档

## 概述

本文档描述了 Chat2DB 项目从前端架构到整体技术栈的演进过程，特别是从前端 Angular 框架迁移到 Svelte 框架的重大变更。

## 原始架构

### 前端技术栈
- 框架: Angular 12+
- 构建工具: Angular CLI
- 状态管理: RxJS
- 包管理: npm
- 语言: TypeScript

### 主要组件
1. QueryComponent - 主要的查询界面组件
2. QueryService - 与后端 API 交互的服务

### 目录结构
```
frontend/
├── src/
│   ├── app/
│   │   ├── query/
│   │   │   ├── query.component.html
│   │   │   ├── query.component.ts
│   │   │   └── query.service.ts
│   │   └── ...
│   └── ...
├── angular.json
└── package.json
```

## 新架构 (Svelte 版本)

### 前端技术栈
- 框架: Svelte 4+
- 构建工具: Vite
- 状态管理: Svelte 内置响应式系统
- 包管理: npm
- 语言: JavaScript/TypeScript

### 主要组件
1. Query.svelte - 主要的查询界面组件
2. api.js - 与后端 API 交互的客户端

### 目录结构
```
svelte-frontend/
├── src/
│   ├── App.svelte
│   ├── Query.svelte
│   ├── api.js
│   ├── app.css
│   ├── main.js
│   └── ...
├── vite.config.js
└── package.json
```

## 迁移优势

### 性能提升
- Svelte 的编译时优化减少了运行时开销
- 更小的包体积，提高加载速度
- 更少的内存占用

### 开发体验改善
- 更简单的状态管理（无需 RxJS）
- 更快的构建速度（Vite 替代 Angular CLI）
- 更直观的组件模型

### 维护性增强
- 更少的样板代码
- 更清晰的代码结构
- 更容易上手的框架学习曲线

## API 兼容性

新架构保持了与后端 API 的完全兼容，所有接口保持不变：

- `/api/query` - 自然语言查询接口
- `/api/chat` - 聊天接口
- `/api/models` - 获取模型列表接口
- `/api/embeddings/encode` - 文本编码为向量
- `/api/embeddings/similarity` - 计算文本相似度

## 部署变更

### Docker 配置更新
docker-compose.yml 文件已更新以使用新的 Svelte 前端服务：

```yaml
services:
  svelte-frontend:
    build:
      context: ./svelte-frontend
      dockerfile: Dockerfile
    # ... 其他配置保持一致
```

### 构建流程变更
- 从 `ng build` 变更为 `vite build`
- 从 Angular 的构建产物变更为 Vite 的构建产物
- 从 Angular 的开发服务器变更为 Vite 的开发服务器

## 测试策略更新

### 单元测试
- 从 Angular 的 TestBed 变更为 Vitest
- 从 Jasmine 变更为 Vitest 断言库
- 从 Karma 变更为 Node.js 环境运行

### 组件测试
- 从 Angular Testing Library 变更为 Svelte Testing Library
- 保持相似的测试模式和 API

## 迁移计划回顾

### 已完成阶段
1. ✅ 环境搭建与基础组件
2. ✅ API 集成
3. ✅ 功能完善与优化
4. ✅ 构建与部署

### 风险控制
- 保持 API 接口不变，确保前后端兼容
- 保留 Angular 版本作为参考实现
- 提供完整的文档说明变更内容

## 未来规划

### 功能扩展
- 添加更多 Svelte 组件以支持完整的功能集
- 集成更高级的状态管理方案（如需要）
- 添加路由支持以支持多页面应用

### 性能优化
- 利用 Svelte 的特性进一步优化组件性能
- 优化构建配置以减小包体积
- 添加代码分割和懒加载

### 测试完善
- 增加更多的单元测试覆盖率
- 添加集成测试验证 API 交互
- 添加端到端测试确保用户体验