# Interest Social API - 部署文档

## 目录

1. [环境要求](#环境要求)
2. [快速开始](#快速开始)
3. [生产环境部署](#生产环境部署)
4. [配置说明](#配置说明)
5. [监控与日志](#监控与日志)
6. [备份与恢复](#备份与恢复)
7. [故障排查](#故障排查)

---

## 环境要求

### 系统要求

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+) / macOS 12+
- **CPU**: 最低 2 核，推荐 4 核以上
- **内存**: 最低 4GB，推荐 8GB 以上
- **磁盘**: 最低 20GB 可用空间

### 软件依赖

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Docker | 24.0+ | 容器运行时 |
| Docker Compose | 2.20+ | 容器编排工具 |
| Git | 2.30+ | 版本控制 |

### 端口要求

| 端口 | 服务 | 说明 |
|------|------|------|
| 80 | Nginx | HTTP 入口 |
| 443 | Nginx | HTTPS 入口 |
| 5000 | API | 应用服务 |
| 5432 | PostgreSQL | 数据库 |
| 6379 | Redis | 缓存服务 |

---

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd interest_social_api
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置：

```bash
# 应用配置
APP_ENV=production
APP_SECRET_KEY=<生成一个安全的密钥>
APP_DEBUG=False

# JWT配置
JWT_SECRET_KEY=<生成一个安全的JWT密钥>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# 数据库配置
DB_PASSWORD=<数据库密码>

# Redis配置
REDIS_PASSWORD=<Redis密码>

# CORS配置
CORS_ORIGINS=https://yourdomain.com
```

### 3. 生成密钥

```bash
# 生成 APP_SECRET_KEY
openssl rand -hex 32

# 生成 JWT_SECRET_KEY
openssl rand -hex 32
```

### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

### 5. 验证部署

```bash
# 健康检查
curl http://localhost:5000/health

# 就绪检查
curl http://localhost:5000/ready

# API 根路径
curl http://localhost:5000/
```

---

## 生产环境部署

### 1. SSL/TLS 证书配置

将 SSL 证书放置在 `nginx/ssl/` 目录：

```
nginx/ssl/
├── cert.pem    # SSL 证书
└── key.pem     # 私钥文件
```

**使用 Let's Encrypt 获取免费证书：**

```bash
# 安装 certbot
apt-get install certbot

# 获取证书
certbot certonly --standalone -d api.yourdomain.com

# 复制证书
cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### 2. 数据库初始化

首次部署时，数据库会自动初始化。如需手动初始化：

```bash
# 进入 PostgreSQL 容器
docker-compose exec postgres psql -U appuser -d interest_social

# 执行初始化脚本
\i /docker-entrypoint-initdb.d/01-init.sql
```

### 3. 生产环境配置

创建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  api:
    image: ghcr.io/your-org/interest-social-api:${VERSION:-latest}
    restart: always
    environment:
      - APP_ENV=production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

启动生产环境：

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. 水平扩展

```bash
# 扩展 API 服务到 3 个实例
docker-compose up -d --scale api=3
```

### 5. 滚动更新

```bash
# 拉取最新镜像
docker-compose pull api

# 重新创建容器（零停机）
docker-compose up -d --no-deps --build api
```

---

## 配置说明

### 环境变量详解

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| APP_ENV | 是 | development | 运行环境 |
| APP_SECRET_KEY | 是 | - | 应用密钥 |
| APP_DEBUG | 否 | False | 调试模式 |
| JWT_SECRET_KEY | 是 | - | JWT 签名密钥 |
| JWT_ALGORITHM | 否 | HS256 | JWT 加密算法 |
| JWT_ACCESS_TOKEN_EXPIRES | 否 | 3600 | 访问令牌有效期(秒) |
| JWT_REFRESH_TOKEN_EXPIRES | 否 | 2592000 | 刷新令牌有效期(秒) |
| DATABASE_URL | 是 | - | 数据库连接字符串 |
| REDIS_URL | 否 | redis://localhost:6379/0 | Redis 连接字符串 |
| LOG_LEVEL | 否 | INFO | 日志级别 |
| CORS_ORIGINS | 否 | * | 允许的跨域来源 |
| RATE_LIMIT_PER_MINUTE | 否 | 60 | 每分钟请求限制 |

### Gunicorn 配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| GUNICORN_WORKERS | CPU核心数*2+1 | Worker 进程数 |
| GUNICORN_THREADS | 2 | 每个 Worker 的线程数 |
| GUNICORN_TIMEOUT | 120 | 请求超时时间(秒) |
| GUNICORN_MAX_REQUESTS | 1000 | 重启前处理的最大请求数 |

---

## 监控与日志

### 日志配置

日志输出到标准输出，可通过 Docker 日志查看：

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看 API 日志
docker-compose logs -f api

# 查看最近 100 行日志
docker-compose logs --tail=100 api
```

### 健康检查端点

| 端点 | 用途 | 响应示例 |
|------|------|----------|
| /health | 存活探针 | `{"status": "healthy"}` |
| /ready | 就绪探针 | `{"status": "ready"}` |

### Prometheus 指标

可集成 Prometheus 进行监控，建议监控指标：

- HTTP 请求延迟 (P50, P95, P99)
- HTTP 请求错误率
- 容器 CPU/内存使用率
- 数据库连接池状态
- Redis 连接状态

---

## 备份与恢复

### 数据库备份

```bash
# 创建备份
docker-compose exec postgres pg_dump -U appuser interest_social > backup_$(date +%Y%m%d).sql

# 恢复备份
cat backup_20240315.sql | docker-compose exec -T postgres psql -U appuser interest_social
```

### 自动备份脚本

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U appuser interest_social > "$BACKUP_DIR/db_$DATE.sql"
find "$BACKUP_DIR" -name "db_*.sql" -mtime +7 -delete
```

---

## 故障排查

### 常见问题

#### 1. 容器启动失败

**症状**: 容器反复重启

**排查步骤**:
```bash
# 查看容器日志
docker-compose logs api

# 查看容器状态
docker-compose ps

# 检查容器退出码
docker inspect interest-social-api | grep -A 5 "State"
```

**常见原因**:
- 环境变量未配置
- 端口被占用
- 依赖服务未就绪

#### 2. 数据库连接失败

**症状**: API 报错 "Connection refused"

**排查步骤**:
```bash
# 检查 PostgreSQL 状态
docker-compose exec postgres pg_isready -U appuser

# 测试数据库连接
docker-compose exec postgres psql -U appuser -d interest_social -c "SELECT 1"

# 检查网络连通性
docker-compose exec api ping postgres
```

**解决方案**:
- 确认数据库容器已启动
- 检查 DATABASE_URL 配置
- 确认数据库用户权限

#### 3. Redis 连接失败

**症状**: 缓存功能不可用

**排查步骤**:
```bash
# 检查 Redis 状态
docker-compose exec redis redis-cli ping

# 检查 Redis 连接
docker-compose exec api curl redis:6379
```

#### 4. JWT 认证失败

**症状**: 返回 401 Unauthorized

**排查步骤**:
```bash
# 检查 JWT 配置
docker-compose exec api env | grep JWT

# 验证 Token 格式
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/auth/me
```

**常见原因**:
- Token 过期
- JWT_SECRET_KEY 配置错误
- Token 格式不正确

#### 5. 性能问题

**症状**: 响应缓慢

**排查步骤**:
```bash
# 检查资源使用
docker stats

# 检查进程状态
docker-compose exec api ps aux

# 查看慢查询日志
docker-compose exec postgres psql -c "SELECT * FROM pg_stat_activity"
```

**优化建议**:
- 增加 Gunicorn workers
- 优化数据库查询
- 启用 Redis 缓存
- 增加容器资源限制

#### 6. SSL 证书问题

**症状**: HTTPS 无法访问

**排查步骤**:
```bash
# 检查证书文件
ls -la nginx/ssl/

# 验证证书
openssl x509 -in nginx/ssl/cert.pem -text -noout

# 测试 SSL 连接
openssl s_client -connect localhost:443
```

### 日志分析

#### 错误日志级别

| 级别 | 说明 | 处理优先级 |
|------|------|-----------|
| CRITICAL | 系统崩溃 | 立即处理 |
| ERROR | 功能异常 | 尽快处理 |
| WARNING | 潜在问题 | 计划处理 |
| INFO | 正常信息 | 无需处理 |

#### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求格式 |
| 401 | 认证失败 | 检查 Token |
| 403 | 权限不足 | 检查用户权限 |
| 404 | 资源不存在 | 检查 URL |
| 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 服务器内部错误 | 查看日志排查 |

### 紧急恢复

```bash
# 重启所有服务
docker-compose restart

# 重建服务
docker-compose up -d --force-recreate

# 回滚到上一版本
docker-compose down
docker tag interest-social-api:latest interest-social-api:backup
docker-compose up -d
```

---

## 联系支持

如遇到无法解决的问题，请提供以下信息：

1. 错误日志 (`docker-compose logs api`)
2. 环境变量配置（脱敏后）
3. 复现步骤
4. 容器状态 (`docker-compose ps`)
