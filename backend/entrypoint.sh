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

# 预加载模型以避免在运行时出现网络问题
echo "Preloading embedding model..."
python3 -c "
import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HF_HUB_OFFLINE'] = '1'
try:
    from embeddings.model import EmbeddingsModel
    model = EmbeddingsModel()
    # 预加载模型
    model.encode('test')
    print('Model preloaded successfully')
except Exception as e:
    print(f'Error preloading model: {e}')
    print('Continuing with default model...')
"

echo "Starting Flask..."
# 以可被外部访问的地址启动
exec python3 /app/app.py