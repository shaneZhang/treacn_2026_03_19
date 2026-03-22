# Interest Social API - Makefile
# Production-grade automation commands

.PHONY: help build up down restart logs test security-scan clean deploy-staging deploy-production

# Default target
help:
	@echo "Interest Social API - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup          - Initial setup (secrets, directories)"
	@echo "  make secrets        - Generate secure secrets"
	@echo "  make dirs           - Create required directories"
	@echo ""
	@echo "Development Commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (follow mode)"
	@echo "  make logs-api       - View API logs only"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test           - Run unit tests"
	@echo "  make test-coverage  - Run tests with coverage"
	@echo "  make lint           - Run code linting"
	@echo "  make security-scan  - Run security scans"
	@echo ""
	@echo "Database Commands:"
	@echo "  make db-backup      - Backup database"
	@echo "  make db-restore     - Restore database (FILE=backup.sql)"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make db-shell       - Open database shell"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make prune          - Prune unused Docker resources"
	@echo "  make update         - Update Docker images"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  make deploy-staging    - Deploy to staging"
	@echo "  make deploy-production - Deploy to production"
	@echo ""
	@echo "Monitoring Commands:"
	@echo "  make health         - Check service health"
	@echo "  make stats          - Show container stats"
	@echo "  make shell          - Open API container shell"

# Setup Commands
setup: secrets dirs
	@echo "Setup complete!"

secrets:
	@echo "Generating secure secrets..."
	@chmod +x scripts/generate-secrets.sh
	@./scripts/generate-secrets.sh

dirs:
	@echo "Creating required directories..."
	@mkdir -p logs data/postgres data/redis data/prometheus data/grafana nginx/logs nginx/ssl
	@chmod 755 logs data
	@chmod 700 data/postgres data/redis
	@echo "Directories created!"

# Development Commands
build:
	@echo "Building Docker images..."
	@docker-compose build --no-cache

up:
	@echo "Starting services..."
	@docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@make health

down:
	@echo "Stopping services..."
	@docker-compose down

restart:
	@echo "Restarting services..."
	@docker-compose restart

logs:
	@docker-compose logs -f

logs-api:
	@docker-compose logs -f api

# Testing Commands
test:
	@echo "Running unit tests..."
	@docker-compose exec -T api pytest tests/ -v

test-coverage:
	@echo "Running tests with coverage..."
	@docker-compose exec -T api pytest --cov=app --cov-report=html --cov-report=term tests/

lint:
	@echo "Running code linting..."
	@docker-compose exec -T api flake8 app/
	@docker-compose exec -T api black --check app/

security-scan:
	@echo "Running security scans..."
	@docker-compose exec -T api bandit -r app/
	@docker run --rm -v $(PWD):/app aquasec/trivy fs /app

# Database Commands
db-backup:
	@echo "Backing up database..."
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U appuser interest_social | gzip > backups/backup_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "Backup complete!"

db-restore:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make db-restore FILE=backup.sql.gz"; \
		exit 1; \
	fi
	@echo "Restoring database from $(FILE)..."
	@gunzip < $(FILE) | docker-compose exec -T postgres psql -U appuser -d interest_social
	@echo "Restore complete!"

db-migrate:
	@echo "Running database migrations..."
	@docker-compose exec api flask db upgrade

db-shell:
	@docker-compose exec postgres psql -U appuser -d interest_social

# Maintenance Commands
clean:
	@echo "Cleaning up..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f

prune:
	@echo "Pruning Docker resources..."
	@docker system prune -af --volumes

update:
	@echo "Updating Docker images..."
	@docker-compose pull
	@docker-compose up -d

# Deployment Commands
deploy-staging:
	@echo "Deploying to staging..."
	@./scripts/deploy.sh staging

deploy-production:
	@echo "Deploying to production..."
	@read -p "Are you sure you want to deploy to production? (yes/no) " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		./scripts/deploy.sh production; \
	else \
		echo "Deployment cancelled."; \
	fi

# Monitoring Commands
health:
	@echo "Checking service health..."
	@curl -fsS http://localhost:5000/health && echo "API is healthy" || echo "API health check failed"
	@docker-compose ps

stats:
	@docker stats --no-stream

shell:
	@docker-compose exec api /bin/sh

# CI/CD Commands (for GitHub Actions)
ci-test:
	@docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit

ci-build:
	@docker build -t interest-social-api:$${GITHUB_SHA:-latest} .

ci-security:
	@docker run --rm -v $(PWD):/app aquasec/trivy fs --exit-code 1 --severity HIGH,CRITICAL /app
