# Chat2DB 部署说明

## 目标
使用 docker-compose 启动完整的 Chat2DB 应用（包括前端和后端），并将 SQLite 数据持久化到宿主机。

## 部署步骤

### 1. 构建并启动完整应用

```bash
cd /path/to/chat2db
docker compose up --build -d
```

### 2. 检查服务健康

后端健康检查：
```bash
curl http://127.0.0.1:5001/health
```

前端访问：
打开浏览器访问 http://localhost

### 3. 停止并移除容器

```bash
docker compose down
```

## 环境变量配置

后端服务支持以下环境变量配置：

- `OLLAMA_URL`: Ollama 服务地址（默认: http://host.docker.internal:11434）
- `OLLAMA_MODEL`: 使用的模型名称（默认: llama2）

## 数据持久化

- `./data` 目录会包含 `chat2db.sqlite`，用于存储应用数据
- 该目录已在 `.gitignore` 中忽略，不会被加入版本控制

## 生产环境部署建议

1. **反向代理**：建议在前端服务前使用 Nginx 或其他反向代理服务器
2. **SSL证书**：为公网访问配置SSL证书
3. **资源限制**：根据实际需求为容器设置内存和CPU限制
4. **备份策略**：定期备份 `./data` 目录中的 SQLite 数据库文件

## 故障排除

### 常见问题

1. **前端无法连接后端**：
   - 检查后端服务是否正常运行
   - 确认网络配置正确

2. **Ollama 连接问题**：
   - 确保 Ollama 服务在 host.docker.internal:11434 上运行
   - 检查防火墙设置

3. **数据库初始化失败**：
   - 检查 `./data` 目录权限
   - 确保容器有写入权限

### 查看日志

```bash
# 查看后端日志
docker compose logs backend

# 查看前端日志
docker compose logs frontend

# 实时查看日志
docker compose logs -f
```
