#!/bin/bash
# Interest Social API - Secret Generation Script
# Generates cryptographically secure secrets for production deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Generating secure secrets for Interest Social API...${NC}"
echo ""

# Check for required tools
command -v openssl >/dev/null 2>&1 || { echo -e "${RED}openssl is required but not installed${NC}"; exit 1; }

# Generate secrets
JWT_SECRET_KEY=$(openssl rand -base64 48)
APP_SECRET_KEY=$(openssl rand -base64 48)
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
SECURITY_PASSWORD_SALT=$(openssl rand -hex 16)
AES_MASTER_KEY=$(openssl rand -base64 32)
AES_SALT=$(openssl rand -hex 16)

# Generate Fernet key using Python
if command -v python3 >/dev/null 2>&1; then
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
elif command -v python >/dev/null 2>&1; then
    ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
else
    echo -e "${YELLOW}Python not found. Using alternative method for Fernet key...${NC}"
    ENCRYPTION_KEY=$(openssl rand -base64 32)
fi

# Generate Grafana password
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 24)

# Create .env file
cat > .env << EOF
# =============================================================================
# Interest Social API - Environment Configuration
# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
# WARNING: This file contains sensitive secrets. Keep it secure!
# =============================================================================

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
APP_ENV=production
APP_SECRET_KEY=$APP_SECRET_KEY
APP_DEBUG=false
APP_VERSION=1.0.0

# -----------------------------------------------------------------------------
# JWT Configuration
# -----------------------------------------------------------------------------
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
JWT_ISSUER=interest-social-api
JWT_AUDIENCE=interest-social-users

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
DB_USER=appuser
DB_PASSWORD=$DB_PASSWORD
DB_NAME=interest_social
DB_HOST=postgres
DB_PORT=5432
DATABASE_URL=postgresql://appuser:$DB_PASSWORD@postgres:5432/interest_social
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# -----------------------------------------------------------------------------
# Redis Configuration
# -----------------------------------------------------------------------------
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0
REDIS_POOL_SIZE=10

# -----------------------------------------------------------------------------
# Encryption Keys
# -----------------------------------------------------------------------------
ENCRYPTION_KEY=$ENCRYPTION_KEY
SECURITY_PASSWORD_SALT=$SECURITY_PASSWORD_SALT
AES_MASTER_KEY=$AES_MASTER_KEY
AES_SALT=$AES_SALT

# -----------------------------------------------------------------------------
# Gunicorn Configuration
# -----------------------------------------------------------------------------
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_BIND_ADDRESS=0.0.0.0
GUNICORN_BIND_PORT=5000
GUNICORN_TIMEOUT=120
GUNICORN_GRACEFUL_TIMEOUT=120
GUNICORN_MAX_REQUESTS=1000
GUNICORN_MAX_REQUESTS_JITTER=50

# -----------------------------------------------------------------------------
# Security Configuration
# -----------------------------------------------------------------------------
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
LOG_LEVEL=INFO
LOG_FORMAT=json

# -----------------------------------------------------------------------------
# Monitoring
# -----------------------------------------------------------------------------
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD
GRAFANA_ROOT_URL=https://grafana.yourdomain.com

# -----------------------------------------------------------------------------
# Deployment Settings
# -----------------------------------------------------------------------------
DATA_DIR=./data
IMAGE_TAG=latest
BUILD_DATE=
VCS_REF=

# -----------------------------------------------------------------------------
# SSL/TLS Configuration
# -----------------------------------------------------------------------------
SSL_CERT_PATH=./nginx/ssl/cert.pem
SSL_KEY_PATH=./nginx/ssl/key.pem

# -----------------------------------------------------------------------------
# Feature Flags
# -----------------------------------------------------------------------------
ENABLE_REGISTRATION=true
ENABLE_PASSWORD_RESET=true
ENABLE_API_KEYS=true
ENABLE_RATE_LIMITING=true
EOF

echo -e "${GREEN}✓ Secrets generated successfully!${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT SECURITY NOTES:${NC}"
echo "============================"
echo "1. The .env file has been created with secure random secrets"
echo "2. Keep the .env file secure and never commit it to version control"
echo "3. Add .env to your .gitignore file"
echo "4. Make regular backups of the .env file in a secure location"
echo "5. Rotate secrets periodically (recommended: every 90 days)"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review and customize the .env file for your environment"
echo "2. Update CORS_ORIGINS with your actual domain"
echo "3. Set up SSL certificates in nginx/ssl/"
echo "4. Run 'make setup' to complete the setup"
echo ""
echo -e "${GREEN}Setup complete!${NC}"
