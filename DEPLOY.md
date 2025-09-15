chat2db 部署说明

目标：以 docker-compose 启动后端并将 sqlite 数据持久化到宿主机。

1) 先构建并启动后端（开发模式）

```bash
cd /path/to/chat2db
docker compose up --build -d backend
```

2) 检查服务健康：

```bash
curl http://127.0.0.1:5001/health
```

3) 停止并移除容器：

```bash
docker compose down
```

注意事项：
- `./data` 目录会包含 `chat2db.sqlite`，请不要把它加入到版本控制（`.gitignore` 已忽略）
- 如果需要把服务暴露在公网，请使用生产级 WSGI 服务（gunicorn/uWSGI）并在前端/反向代理（nginx）下运行
- 若要构建前端容器：在本地构建 Angular 应用并把产物放到 `./frontend_dist`，docker-compose 已提供 nginx 占位服务用于静态托管
