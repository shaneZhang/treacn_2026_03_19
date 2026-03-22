# 生产级Dockerfile - 多阶段构建
# 第一阶段：构建阶段
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# 设置构建环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖到虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 第二阶段：生产阶段
FROM python:3.12-slim-bookworm AS production

WORKDIR /app

# 设置生产环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 创建非root用户
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /bin/bash appuser

# 安装生产依赖（仅安装必要的系统包）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 复制应用代码
COPY . .

# 设置正确的权限
RUN chown -R appuser:appgroup /app && \
    chmod -R 755 /app

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 暴露端口
EXPOSE 5000

# 使用Gunicorn作为生产级WSGI服务器
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
    "--workers", "4", \
    "--threads", "2", \
    "--timeout", "120", \
    "--keepalive", "5", \
    "--max-requests", "1000", \
    "--max-requests-jitter", "200", \
    "run:app"]