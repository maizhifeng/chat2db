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

- Angular 12+
- TypeScript
- HTML/CSS
- RxJS

## 安装和运行

1. 确保已安装Node.js和npm
2. 安装Angular CLI: `npm install -g @angular/cli`
3. 进入前端目录: `cd frontend`
4. 安装依赖: `npm install`
5. 启动开发服务器: `ng serve`
6. 访问应用: http://localhost:4200

## 架构说明

### 组件结构

- `app/` - 主应用组件
  - `components/` - 各功能组件
    - `auth/` - 认证相关组件
    - `dashboard/` - 仪表板组件
    - `ai-assistant/` - AI助手组件
    - `sql-editor/` - SQL编辑器组件
    - `data-browser/` - 数据浏览器组件
    - `connection-manager/` - 连接管理组件
    - `table-manager/` - 表管理组件
  - `services/` - 服务层
  - `guards/` - 路由守卫

### 路由配置

应用包含以下路由：
- `/dashboard` - 仪表板
- `/query` - 基础查询
- `/ai-assistant` - AI助手
- `/sql-editor` - SQL编辑器
- `/data-browser` - 数据浏览器
- `/connections` - 连接管理
- `/tables` - 表管理
- `/login` - 登录
- `/register` - 注册

## 付费版功能

1. **AI助手集成** - 与Ollama等AI模型集成，支持自然语言数据库查询
2. **增强SQL编辑器** - 包含代码补全、语法高亮、格式化等功能
3. **数据浏览器** - 可视化数据浏览，支持过滤、排序、分页和导出
4. **高级连接管理** - 支持多种数据库类型（SQLite, MySQL, PostgreSQL等）
5. **用户友好的仪表板** - 直观的统计数据展示和快速导航

## 开发说明

1. 所有组件都遵循Angular的最佳实践
2. 使用服务层进行HTTP请求和业务逻辑处理
3. 实现了路由守卫确保应用安全性
4. 响应式设计适配不同屏幕尺寸

## 注意事项

1. 后端API需要在`http://localhost:5001`运行
2. 确保后端服务正确配置了数据库连接
3. AI功能需要Ollama服务支持