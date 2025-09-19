# 前端迁移到 Svelte 框架设计文档

## 1. 概述

### 1.1 项目背景
当前 Chat2DB 前端采用 Angular 框架构建，为了提升性能、减小包体积并改善开发体验，计划将前端框架迁移到 Svelte。

### 1.2 迁移目标
- 将现有的 Angular 组件和功能迁移到 Svelte 框架
- 保持现有功能完整性和用户体验一致性
- 利用 Svelte 的编译时优化提升应用性能
- 减少最终打包体积，提高加载速度

### 1.3 迁移范围
- 将现有的 `query.component` 重构为 Svelte 组件
- 保持与后端 API 的交互不变
- 重构前端构建流程以适应 Svelte

## 2. 技术架构

### 2.1 当前架构分析
当前前端架构基于 Angular，包含以下关键组件：
- QueryComponent: 主要的查询界面组件
- QueryService: 与后端 API 交互的服务

### 2.2 Svelte 架构设计
迁移后的架构将采用 Svelte 的组件化结构：
- Query.svelte: 主要查询界面组件
- api.js: 封装与后端交互的 API 调用
- stores.js: 状态管理（如需要）

### 2.3 技术选型
- 框架: Svelte 4.x
- 构建工具: Vite
- 包管理: npm
- 状态管理: Svelte 内置响应式系统（必要时引入 Pinia）

## 3. 组件架构

### 3.1 组件定义

#### 3.1.1 Query 组件 (主要组件)
该组件负责处理用户输入的自然语言查询，并显示结果。

**Props:**
- 无

**State:**
- queryText: 用户输入的查询文本
- results: 查询结果数组
- sql: 生成的 SQL 语句
- loading: 加载状态标识
- models: 可用模型列表
- selectedModel: 当前选择的模型
- loadingModels: 模型加载状态
- loadingMessage: 加载提示信息
- retryCount: 重试次数

**事件处理:**
- onMount: 组件挂载时获取模型列表
- send: 发送自然语言查询
- loadModelAndChat: 使用指定模型发送聊天请求

### 3.2 组件层级结构
```
App
└── Query (主要组件)
```

### 3.3 状态管理
使用 Svelte 内置的响应式系统管理组件状态，对于全局状态可考虑使用 stores。

## 4. API 集成层

### 4.1 API 客户端重构
将现有的 Angular HttpClient 调用重构为基于 fetch API 的调用。

### 4.2 接口定义
保持与后端 API 接口一致:
- `/api/query` - 自然语言查询接口
- `/api/chat` - 聊天接口
- `/api/models` - 获取模型列表接口
- `/api/embeddings/encode` - 文本编码为向量
- `/api/embeddings/similarity` - 计算文本相似度

## 5. 构建与部署

### 5.1 构建流程
使用 Vite 作为构建工具，配置如下：
- 开发环境: `vite`
- 生产构建: `vite build`

### 5.1.1 环境兼容性检查
在构建之前，需要检查当前开发环境是否兼容 Svelte 4.x 和 Vite 4.x：
- Node.js 版本 >= 16.x
- npm 版本 >= 8.x

### 5.1.2 环境升级方案
如果环境不兼容，需要进行升级：
1. 升级 Node.js:
   - 检查当前版本: `node --version`
   - 如果版本低于 16.x，需要升级 Node.js
   - 推荐使用 nvm (Node Version Manager) 进行版本管理
   
2. 升级 npm:
   - 检查当前版本: `npm --version`
   - 如果版本低于 8.x，升级 npm: `npm install -g npm@latest`
   
3. 全局工具升级:
   - 卸载旧版本的构建工具: `npm uninstall -g @angular/cli`
   - 安装必要的全局工具: `npm install -g vite vitest`

### 5.2 部署配置
保持现有的 Docker 部署方式，更新 Dockerfile 以适应 Svelte 构建产物。

## 6. 迁移计划

### 6.1 迁移步骤

#### 第一阶段：环境搭建与基础组件
1. 初始化 Svelte 项目结构
2. 配置 Vite 构建工具
3. 创建基础 Query 组件框架
4. 实现基本的 UI 结构

#### 第二阶段：API 集成
1. 重构 QueryService 为 Svelte 版本的 API 客户端
2. 实现查询功能
3. 实现模型选择功能
4. 实现聊天功能

#### 第三阶段：功能完善与优化
1. 实现加载状态和错误处理
2. 优化组件性能
3. 添加必要的动画和过渡效果
4. 进行完整的功能测试

#### 第四阶段：构建与部署
1. 配置生产构建
2. 更新 Dockerfile
3. 验证部署流程
4. 进行端到端测试

### 6.2 风险评估与应对措施
- 功能兼容性风险：通过充分的测试确保功能一致性
- 性能问题：利用 Svelte 的编译时优化提升性能
- 集成问题：保持 API 接口不变，确保前后端兼容

## 7. 测试策略

### 7.1 单元测试
使用 Vitest 进行组件和逻辑的单元测试。

### 7.2 集成测试
验证与后端 API 的集成是否正常工作。

### 7.3 端到端测试
使用 Cypress 进行端到端测试，确保用户流程完整。