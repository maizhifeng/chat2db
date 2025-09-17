FROM python:3.11.13-trixie

WORKDIR /app

# 安装构建工具和证书
RUN apt-get update && apt-get install -y --no-install-recommends gcc git ca-certificates && rm -rf /var/lib/apt/lists/*

# 设置环境变量以解决SSL连接问题
ENV CURL_CA_BUNDLE=""
ENV REQUESTS_CA_BUNDLE=""
ENV HF_HUB_OFFLINE="1"

# 复制依赖文件并安装
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制应用代码
COPY . /app

# 创建数据目录（挂载点）
VOLUME ["/data"]

# 赋予入口脚本执行权限
RUN chmod +x /app/entrypoint.sh

EXPOSE 5001

ENTRYPOINT ["/app/entrypoint.sh"]