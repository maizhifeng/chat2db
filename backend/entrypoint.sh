#!/bin/bash
set -e

# 确保挂载目录存在
mkdir -p /data

# 初始化数据库（仅在首次运行或文件不存在时）
if [ ! -f /data/chat2db.sqlite ]; then
  echo "Initializing DB..."
  # init_db.py 会写入 /data/chat2db.sqlite
  python3 /app/init_db.py
fi

echo "Starting Flask..."
# 以可被外部访问的地址启动
exec python3 /app/app.py
