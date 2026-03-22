# Interest Social API 部署指南

## 目录
1. [项目概述](#项目概述)
2. [环境要求](#环境要求)
3. [快速部署](#快速部署)
4. [生产环境部署](#生产环境部署)
5. [开发环境部署](#开发环境部署)
6. [配置说明](#配置说明)
7. [安全加固指南](#安全加固指南)
8. [监控和日志](#监控和日志)
9. [故障排查](#故障排查)
10. [常见问题](#常见问题)

## 项目概述

Interest Social API 是一个社交平台后端API服务，提供用户认证、内容管理、消息推送等功能。

## 环境要求

### 最低配置
- CPU: 2核
- 内存: 2GB
- 磁盘: 20GB SSD

### 推荐配置（生产环境）
- CPU: 4核
- 内存: 8GB
- 磁盘: 50GB SSD

### 软件依赖
- Docker: 24.0+
- Docker Compose: 2.20+
- Python: 3.10+ (仅开发环境需要)

## 快速部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd interest_social_api
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，修改敏感配置
```

### 3. 启动服务
```bash
# 生产环境（启动API和Nginx）
docker-compose up -d

# 仅启动API服务
docker-compose up -d api
```

### 4. 验证部署
```bash
# 检查服务状态
docker-compose ps

# 检查健康状态
curl http://localhost:5000/

# 预期输出: {"code":200,"message":"Welcome to Interest Social API",...}
```

## 生产环境部署

### 1. 安全配置

#### 生成密钥
```bash
# 进入Python环境生成安全密钥
python3 -c "
from cryptography.fernet import Fernet
import secrets

print('SECRET_KEY:', secrets.token_urlsafe(32))
print('JWT_SECRET_KEY:', secrets.token_urlsafe(32))
print('ENCRYPTION_KEY:', Fernet.generate_key().decode())
print('API_KEY:', secrets.token_urlsafe(32))
"
```

#### 更新环境变量
编辑 `.env` 文件：
```env
# Flask配置
FLASK_APP=run.py
FLASK_ENV=production
FLASK_DEBUG=False

# 密钥配置（使用上面生成的值
SECRET_KEY=your-generated-secret-key-here
JWT_SECRET_KEY=your-generated-jwt-secret-key-here
ENCRYPTION_KEY=your-generated-encryption-key-here

# JWT过期时间配置
JWT_ACCESS_TOKEN_EXPIRES=15
JWT_REFRESH_TOKEN_EXPIRES=7

# CORS配置（生产环境修改为具体域名
CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com

# 会话安全配置
SESSION_COOKIE_SECURE=True
```

### 2. SSL证书配置

#### 使用Let's Encrypt
```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d api.your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/api.your-domain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/api.your-domain.com/privkey.pem ./nginx/ssl/
```

#### 配置Nginx HTTPS
编辑 `nginx/conf.d/api.conf`，取消HTTPS配置注释并修改域名。

### 3. 启动生产环境服务
```bash
# 构建并启动
docker-compose build --no-cache
docker-compose up -d

# 验证所有服务正常运行
docker-compose ps
# 预期输出:
# Name                        Command               State                    Ports                  
# ----------------------------------------------------------------------------------------------------
# interest-social-api      /opt/venv/bin/gunicorn ...   Up      0.0.0.0:5000->5000/tcp
# interest-social-nginx   /docker-entrypoint.sh ngin    Up      0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

## 开发环境部署

### 1. 使用Docker Compose（推荐）
```bash
# 启动开发环境服务（支持热重载
docker-compose --profile dev up -d api-dev

# 查看日志
docker-compose logs -f api-dev
```

### 2. 本地Python环境
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
flask run --debug
```

## 配置说明

### Docker Compose 服务说明

| 服务名 | 说明 | 端口 | 配置文件 |
|--------|------|------|---------|
| api | 生产环境API服务 | 5000 | Dockerfile |
| nginx | 反向代理服务器 | 80, 443 | nginx/nginx.conf |
| api-dev | 开发环境API服务 | 5001 | Dockerfile.dev |

### 资源限制配置

默认资源限制：
- API服务: 2核CPU, 512MB内存
- Nginx服务: 1核CPU, 256MB内存

根据服务器配置修改 `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

## 安全加固指南

### 1. 容器安全

#### 使用seccomp配置文件
```bash
# 在docker-compose.yml中添加seccomp配置
security_opt:
  - seccomp:docker/seccomp-profile.json
  - no-new-privileges:true
```

#### 只读根文件系统
已在 `docker-compose.yml` 中配置:
```yaml
read_only: true
tmpfs:
  - /tmp
  - /var/run
```

### 2. 系统级安全

#### 配置防火墙
```bash
# UFW配置
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

#### 禁用不必要的服务
```bash
sudo systemctl stop rpcbind
sudo systemctl disable rpcbind
```

### 3. 应用安全

#### JWT认证
所有敏感接口默认需要JWT认证：
```bash
# 获取Token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}'

# 使用Token访问受保护接口
curl -H "Authorization: Bearer <your-token>" \
  http://localhost:5000/api/home
```

#### API密钥认证（服务间调用）
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/some-internal-endpoint
```

## 监控和日志

### 查看容器日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f nginx

# 查看最近100行日志
docker-compose logs --tail=100 api
```

### 查看资源使用情况
```bash
# 查看容器资源使用
docker stats

# 格式化输出
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

### 健康检查
```bash
# 检查容器健康状态
docker inspect --format '{{.State.Health.Status}}' interest-social-api

# 手动健康检查
curl http://localhost:5000/health
```

## 故障排查

### 常见错误及解决方案

#### 1. 容器无法启动
**症状**: `docker-compose ps` 显示 State 为 Exit

**排查步骤**:
```bash
# 查看容器日志
docker-compose logs api

# 检查端口占用
sudo lsof -i :5000
sudo netstat -tulpn | grep :5000

# 检查配置文件语法
docker-compose config
```

**常见原因**:
- 端口被占用: 修改 `docker-compose.yml` 中的端口映射
- 配置文件错误: 检查 `.env` 和 `config/__init__.py`
- 权限问题: 确保日志目录有写入权限

#### 2. JWT认证失败
**症状**: API返回 401 Unauthorized

**排查步骤**:
```bash
# 检查Token格式是否正确
echo $TOKEN | wc -c  # 应该大于100字符

# 检查Token是否过期
# 使用jwt.io解码Token检查exp字段

# 验证JWT_SECRET_KEY配置是否正确
python3 -c "from config import Config; print(Config.JWT_SECRET_KEY)"
```

**解决方案**:
- 确保请求头格式正确: `Authorization: Bearer <token>`
- 检查服务器时间是否同步
- 验证JWT_SECRET_KEY配置一致性

#### 3. 数据库连接失败（如果使用数据库）
**症状**: 应用日志显示数据库连接错误

**排查步骤**:
```bash
# 检查数据库服务是否运行
docker-compose ps db

# 检查网络连通性
docker exec -it interest-social-api ping db-host

# 验证数据库凭据
mysql -u user -p -h db-host
```

#### 4. Nginx 502 Bad Gateway
**症状**: 通过Nginx访问返回502错误

**排查步骤**:
```bash
# 检查API服务是否正常运行
curl http://localhost:5000/  # 直接访问API

# 检查Nginx配置是否正确
docker exec -it interest-social-nginx nginx -t

# 检查Nginx与API的网络连通性
docker exec -it interest-social-nginx curl http://api:5000/

# 查看Nginx错误日志
docker-compose logs nginx
```

**常见原因**:
- API服务未正常启动
- 网络配置错误: 检查容器是否在同一网络
- 上游配置错误: 检查 `nginx/conf.d/api.conf` 中的 upstream 配置

#### 5. 加密密钥错误
**症状**: 应用启动失败，显示 "Fernet key must be 32 url-safe base64-encoded bytes"

**解决方案**:
```bash
# 生成正确格式的密钥
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 更新 .env 文件中的 ENCRYPTION_KEY
```

### 故障排查流程

```
应用异常
    |
    v
检查容器状态 -> docker-compose ps
    |
    +--> 容器未运行？ ---> 查看日志: docker-compose logs <service>
    |         |
    |         +--> 配置错误？ ---> 验证配置: docker-compose config
    |         |
    |         +--> 依赖服务问题？ ---> 检查依赖服务状态
    |
    v
容器运行正常？
    |
    +--> 是 ---> 检查应用日志: docker-compose logs -f --tail=50 <service>
    |         |
    |         +--> 错误信息？ ---> 根据错误信息搜索解决方案
    |         |
    |         +--> 资源不足？ ---> docker stats
    |
    v
网络层面排查
    |
    +--> 端口监听正常？ ---> netstat -tulpn | grep :<port>
    |
    +--> 防火墙配置？ ---> ufw status / iptables -L
    |
    +--> 外部连通性？ ---> curl <endpoint> 从外部机器访问
    |
    v
回滚到上一个稳定版本
```

### 紧急恢复步骤

#### 1. 服务完全不可用
```bash
# 停止所有服务
docker-compose down

# 检查是否有残留进程
docker ps -a
docker rm -f $(docker ps -aq)  # 谨慎操作！

# 重新启动
docker-compose up -d

# 如仍有问题，回滚到上一个镜像版本
# 修改 docker-compose.yml 中的 image 标签到上一个版本
# docker-compose up -d --force-recreate
```

#### 2. 数据恢复（如果使用持久化存储）
```bash
# 查看数据卷
docker volume ls

# 备份数据卷
docker run --rm -v app_data:/data -v $(pwd):/backup alpine tar cvf /backup/backup.tar /data

# 恢复数据
docker run --rm -v app_data:/data -v $(pwd):/backup alpine tar xvf /backup/backup.tar -C /data --strip 1
```

## 常见问题

### Q: 如何修改JWT过期时间？
A: 修改 `.env` 文件中的 `JWT_ACCESS_TOKEN_EXPIRES`（分钟）和 `JWT_REFRESH_TOKEN_EXPIRES`（天）。

### Q: 如何添加新的API密钥？
A: 修改 `.env` 文件中的 `API_KEY`，或实现多API密钥管理功能。

### Q: 如何开启调试模式？
A: 生产环境不推荐开启，开发环境可设置 `FLASK_DEBUG=True`。

### Q: 容器时间与主机不同步？
A: 确保主机时区正确，或在 `docker-compose.yml` 中添加：
```yaml
volumes:
  - /etc/timezone:/etc/timezone:ro
  - /etc/localtime:/etc/localtime:ro
```

### Q: 如何配置日志轮转？
A: Docker默认已配置日志轮转，可在 `/etc/docker/daemon.json` 中自定义：
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "5"
  }
}
```

## 联系支持

如遇文档未覆盖的问题，请：
1. 收集相关日志和错误信息
2. 记录问题复现步骤
3. 提供环境配置信息
4. 联系开发/运维团队