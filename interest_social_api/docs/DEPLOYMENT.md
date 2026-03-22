# Interest Social API - Production Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Security Setup](#security-setup)
3. [Deployment Steps](#deployment-steps)
4. [Configuration](#configuration)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Prerequisites

### System Requirements
- Docker Engine 24.0+
- Docker Compose 2.20+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space
- Linux/macOS/Windows with WSL2

### Required Tools
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

---

## Security Setup

### 1. Generate Secure Secrets

Create a script to generate all required secrets:

```bash
#!/bin/bash
# generate-secrets.sh

echo "Generating secure secrets..."

# Generate JWT secret (32+ characters)
export JWT_SECRET_KEY=$(openssl rand -base64 48)

# Generate app secret
export APP_SECRET_KEY=$(openssl rand -base64 48)

# Generate database password
export DB_PASSWORD=$(openssl rand -base64 32)

# Generate Redis password
export REDIS_PASSWORD=$(openssl rand -base64 32)

# Generate Fernet encryption key
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Generate password salt
export SECURITY_PASSWORD_SALT=$(openssl rand -hex 16)

# Generate AES keys
export AES_MASTER_KEY=$(openssl rand -base64 32)
export AES_SALT=$(openssl rand -hex 16)

# Output to .env file
cat > .env << EOF
# Auto-generated secrets - $(date -u +%Y-%m-%dT%H:%M:%SZ)
APP_ENV=production
APP_SECRET_KEY=$APP_SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
DB_PASSWORD=$DB_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
ENCRYPTION_KEY=$ENCRYPTION_KEY
SECURITY_PASSWORD_SALT=$SECURITY_PASSWORD_SALT
AES_MASTER_KEY=$AES_MASTER_KEY
AES_SALT=$AES_SALT
EOF

echo "Secrets generated and saved to .env"
echo "IMPORTANT: Keep .env file secure and never commit it to version control!"
```

Run the script:
```bash
chmod +x generate-secrets.sh
./generate-secrets.sh
```

### 2. SSL/TLS Certificate Setup

#### Option A: Let's Encrypt (Production)
```bash
# Install certbot
sudo apt-get update
sudo apt-get install -y certbot

# Generate certificate
sudo certbot certonly --standalone -d api.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem ./nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem ./nginx/ssl/key.pem

# Set permissions
sudo chmod 644 ./nginx/ssl/cert.pem
sudo chmod 600 ./nginx/ssl/key.pem
```

#### Option B: Self-Signed (Development)
```bash
mkdir -p ./nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./nginx/ssl/key.pem \
  -out ./nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=api.yourdomain.com"
```

### 3. Directory Structure Setup

```bash
# Create required directories
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/prometheus
mkdir -p data/grafana
mkdir -p nginx/logs
mkdir -p nginx/ssl

# Set permissions
chmod 755 logs
chmod 755 data
chmod 700 data/postgres
chmod 700 data/redis
```

---

## Deployment Steps

### 1. Clone and Prepare

```bash
# Clone repository
git clone https://github.com/yourorg/interest-social-api.git
cd interest-social-api

# Generate secrets
./generate-secrets.sh

# Create required directories
mkdir -p logs data/postgres data/redis nginx/ssl
```

### 2. Build and Deploy

```bash
# Build images
docker-compose build

# Start services in detached mode
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f api
```

### 3. Database Initialization

```bash
# Run database migrations (if using Alembic)
docker-compose exec api flask db upgrade

# Or run init script
docker-compose exec postgres psql -U appuser -d interest_social -f /docker-entrypoint-initdb.d/01-init.sql
```

### 4. Health Check

```bash
# Check API health
curl -f http://localhost:5000/health

# Check all services
docker-compose ps

# View logs
docker-compose logs --tail=100
```

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `APP_ENV` | Environment (development/staging/production) | Yes | production |
| `APP_SECRET_KEY` | Application secret key | Yes | - |
| `JWT_SECRET_KEY` | JWT signing key | Yes | - |
| `DB_PASSWORD` | Database password | Yes | - |
| `REDIS_PASSWORD` | Redis password | Yes | - |
| `ENCRYPTION_KEY` | Data encryption key | Yes | - |
| `CORS_ORIGINS` | Allowed CORS origins | Yes | - |

### Docker Compose Profiles

```bash
# Basic deployment (API + DB + Redis + Nginx)
docker-compose up -d

# With monitoring (adds Prometheus + Grafana)
docker-compose --profile monitoring up -d

# Development mode (with hot reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Scaling

```bash
# Scale API workers
docker-compose up -d --scale api=3

# Note: Requires load balancer configuration
```

---

## Monitoring

### 1. Health Endpoints

- `GET /health` - Application health
- `GET /ready` - Readiness probe
- `GET /metrics` - Prometheus metrics (if enabled)

### 2. Log Aggregation

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100 api
```

### 3. Monitoring Stack (Optional)

Access monitoring tools:
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### 4. Alerting Setup

Configure alerts in `monitoring/alertmanager.yml`:

```yaml
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

---

## Troubleshooting

### Common Issues

#### 1. Container Fails to Start

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs <service-name>

# Check for port conflicts
sudo netstat -tulpn | grep 5000

# Restart specific service
docker-compose restart api
```

#### 2. Database Connection Issues

```bash
# Test database connection
docker-compose exec api python -c "
import psycopg2
conn = psycopg2.connect('$DATABASE_URL')
print('Connection successful')
conn.close()
"

# Check PostgreSQL logs
docker-compose logs postgres

# Verify database exists
docker-compose exec postgres psql -U appuser -l
```

#### 3. Redis Connection Issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Verify Redis authentication
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

#### 4. SSL/TLS Issues

```bash
# Verify certificate
docker-compose exec nginx openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout

# Check certificate expiration
docker-compose exec nginx openssl x509 -in /etc/nginx/ssl/cert.pem -noout -dates

# Test SSL connection
curl -v https://localhost/health --insecure
```

#### 5. High Memory Usage

```bash
# Check container resource usage
docker stats

# View memory usage by process
docker-compose exec api ps aux --sort=-%mem

# Restart if needed
docker-compose restart api
```

#### 6. Rate Limiting Issues

```bash
# Check Redis for rate limit keys
docker-compose exec redis redis-cli keys "rate_limit:*"

# Clear rate limit (emergency only)
docker-compose exec redis redis-cli flushdb
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose up -d

# Access container shell
docker-compose exec api /bin/sh

# Run Python shell
docker-compose exec api python

# Check environment variables
docker-compose exec api env | grep -E "(APP_|JWT_|DB_|REDIS_)"
```

---

## Maintenance

### Regular Tasks

#### Daily
```bash
# Check service health
curl -f http://localhost:5000/health

# Check disk space
df -h

# Review error logs
docker-compose logs --tail=100 api | grep ERROR
```

#### Weekly
```bash
# Update images
docker-compose pull
docker-compose up -d

# Clean up unused resources
docker system prune -f

# Backup database
docker-compose exec postgres pg_dump -U appuser interest_social > backup_$(date +%Y%m%d).sql
```

#### Monthly
```bash
# Rotate logs
docker-compose exec api logrotate -f /etc/logrotate.conf

# Update SSL certificates (if using Let's Encrypt)
sudo certbot renew

# Security updates
sudo apt-get update && sudo apt-get upgrade -y
```

### Backup and Recovery

#### Database Backup
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker-compose exec -T postgres pg_dump \
  -U appuser \
  -d interest_social \
  | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

#### Database Restore
```bash
# Restore from backup
gunzip < backup_20240101_120000.sql.gz | \
  docker-compose exec -T postgres psql -U appuser -d interest_social
```

### Security Updates

```bash
# Update base images
docker-compose build --no-cache

# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image interest-social-api:latest

# Apply updates
docker-compose up -d
```

---

## Production Checklist

Before going live, verify:

- [ ] All secrets are generated and stored securely
- [ ] SSL certificates are valid and not expired
- [ ] Database backups are configured
- [ ] Monitoring and alerting are set up
- [ ] Rate limiting is enabled
- [ ] Security headers are configured
- [ ] CORS origins are properly restricted
- [ ] Log rotation is configured
- [ ] Health checks are responding correctly
- [ ] CI/CD pipeline is tested
- [ ] Rollback procedure is documented
- [ ] On-call rotation is established

---

## Support

For issues and support:
- GitHub Issues: https://github.com/yourorg/interest-social-api/issues
- Documentation: https://docs.yourdomain.com
- Email: sre@yourdomain.com
