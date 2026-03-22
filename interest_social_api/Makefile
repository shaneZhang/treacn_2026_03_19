.PHONY: help build up down logs clean test lint security deploy

help:
	@echo "Interest Social API - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build    Build Docker images"
	@echo "  up       Start all services"
	@echo "  down     Stop all services"
	@echo "  logs     View service logs"
	@echo "  clean    Remove containers and volumes"
	@echo "  test     Run tests"
	@echo "  lint     Run code linting"
	@echo "  security Run security scan"
	@echo "  deploy   Deploy to production"
	@echo "  backup   Backup database"
	@echo "  restore  Restore database"

build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	@echo "Services started. API available at http://localhost:5000"

down:
	docker-compose down

logs:
	docker-compose logs -f api

clean:
	docker-compose down -v --rmi local
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +

test:
	docker-compose exec api pytest -v --cov=app --cov-report=term-missing

lint:
	docker-compose exec api flake8 . --count --show-source --statistics
	docker-compose exec api black --check .
	docker-compose exec api isort --check-only .

security:
	chmod +x scripts/security-scan.sh
	./scripts/security-scan.sh

deploy:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps --build api

backup:
	@echo "Creating database backup..."
	docker-compose exec -T postgres pg_dump -U appuser interest_social > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup completed"

restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup filename: " filename; \
	cat $$filename | docker-compose exec -T postgres psql -U appuser interest_social
	@echo "Restore completed"

health:
	curl -f http://localhost:5000/health || exit 1

redis-cli:
	docker-compose exec redis redis-cli

psql:
	docker-compose exec postgres psql -U appuser -d interest_social

shell:
	docker-compose exec api /bin/bash
