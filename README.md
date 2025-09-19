# Chat2DB 增强版前端

这是一个复刻并增强的Chat2DB前端应用，包含了付费版功能。

## 功能特性

1. **仪表板** - 用户概览和快速导航
2. **AI助手** - 集成自然语言处理和AI模型对话
3. **SQL编辑器** - 增强的SQL查询功能，支持代码补全和格式化
4. **数据浏览器** - 表结构查看和数据浏览功能
5. **连接管理** - 多数据库连接管理
6. **表管理** - 数据库表结构管理

## 技术栈

- Angular 12+ (原版本)
- Svelte 4+ (新版本)
- TypeScript
- HTML/CSS
- RxJS (Angular版本)

## 前端迁移说明

为了提升性能、减小包体积并改善开发体验，我们已将前端框架从 Angular 迁移到 Svelte。

### 迁移内容

1. **框架迁移** - 从 Angular 迁移到 Svelte
2. **构建工具** - 从 Angular CLI 迁移到 Vite
3. **组件重构** - 将 Angular 组件重构为 Svelte 组件
4. **状态管理** - 使用 Svelte 内置响应式系统替代 RxJS
5. **API 集成** - 重构为基于 fetch API 的调用

### 目录结构

- `frontend/` - 旧的 Angular 前端代码（保留作为参考）
- `svelte-frontend/` - 新的 Svelte 前端代码（当前使用）

## 最新优化

### AI对话交互优化

我们对AI助手组件进行了全面的界面和交互优化：

1. **消息类型差异化显示**
   - 用户消息：右侧对齐，蓝色背景
   - AI普通回复：左侧对齐，白色背景
   - AI思考过程：左侧对齐，浅黄色背景，带特殊标识
   - 错误消息：左侧对齐，浅红色背景
   - 系统消息：居中显示，灰色背景

2. **思考模式内容特殊显示**
   - 单独的消息类型用于显示AI的思考过程
   - 流式更新显示AI的逐步思考
   - 特殊的视觉标识（脑图图标）
   - 加载动画增强用户体验

3. **加载状态优化**
   - 更清晰的加载状态指示器
   - 分阶段显示处理过程
   - 脉冲动画增强视觉反馈

4. **长消息处理**
   - 智能折叠机制，根据内容长度自动折叠
   - 代码块特殊处理，提供更好的可读性
   - 展开/收起按钮

5. **界面美化**
   - 现代化设计风格
   - 圆角设计和阴影效果
   - 响应式布局适配移动端

## 安装和运行

### Node.js 环境准备

如果系统中尚未安装 Node.js，请运行以下脚本安装：

```bash
./install-node.sh
```

### Svelte 前端运行

1. 进入 Svelte 前端目录: `cd svelte-frontend`
2. 安装依赖: `npm install`
3. 启动开发服务器: `npm run dev`
4. 访问应用: http://localhost:3000

### Angular 前端运行（仅作参考）

1. 确保已安装Node.js和npm
2. 安装Angular CLI: `npm install -g @angular/cli`
3. 进入前端目录: `cd frontend`
4. 安装依赖: `npm install`
5. 启动开发服务器: `ng serve`
6. 访问应用: http://localhost:4200

## 架构说明

### 组件结构

- `svelte-frontend/` - Svelte 前端
  - `src/` - 主源码目录
    - `App.svelte` - 主应用组件
    - `Query.svelte` - 查询组件
    - `api.js` - API 客户端
    - `app.css` - 全局样式
    - `main.js` - 应用入口
  - `src/environments/` - 环境配置
  - `src/__tests__/` - 测试文件

### 路由配置

应用包含以下路由：
- `/` - 主查询界面

## 付费版功能

1. **AI助手集成** - 与Ollama等AI模型集成，支持自然语言数据库查询
2. **增强SQL编辑器** - 包含代码补全、语法高亮、格式化等功能
3. **数据浏览器** - 可视化数据浏览，支持过滤、排序、分页和导出
4. **高级连接管理** - 支持多种数据库类型（SQLite, MySQL, PostgreSQL等）
5. **用户友好的仪表板** - 直观的统计数据展示和快速导航

## 开发说明

1. 所有组件都遵循Svelte的最佳实践
2. 使用基于fetch的API客户端进行HTTP请求
3. 响应式设计适配不同屏幕尺寸

## 注意事项

1. 后端API需要在`http://localhost:5001`运行
2. 确保后端服务正确配置了数据库连接
3. AI功能需要Ollama服务支持

## 部署

### Docker Compose 部署（推荐）

```bash
# 构建并启动所有服务
docker compose up --build -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

### 访问应用

- 前端界面：http://localhost
- 后端API：http://localhost:5001

### 生产环境部署建议

1. 使用反向代理（如 Nginx）处理 SSL 终止
2. 配置合适的资源限制
3. 定期备份数据目录（`./data`）
4. 监控服务日志和性能