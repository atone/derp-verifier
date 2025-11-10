FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装 tailscale
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://tailscale.com/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install --no-cache-dir aiohttp

# 复制应用代码
COPY main.py .

# 暴露端口
EXPOSE 8080

# 启动应用
CMD ["python", "main.py"]
