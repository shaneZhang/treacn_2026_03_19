#!/bin/bash

set -e

echo "========================================="
echo "Interest Social API - Security Scan"
echo "========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "[1/6] Running Bandit (Python Security Linter)..."
if command -v bandit &> /dev/null; then
    bandit -r . -x ./tests,./.git,./__pycache__,./venv -ll -f json -o security-reports/bandit-report.json || true
    echo "✓ Bandit scan completed"
else
    echo "⚠ Bandit not installed, skipping..."
fi

echo ""
echo "[2/6] Running Safety (Dependency Vulnerability Check)..."
if command -v safety &> /dev/null; then
    safety check -r requirements.txt --json > security-reports/safety-report.json 2>&1 || true
    echo "✓ Safety scan completed"
else
    echo "⚠ Safety not installed, skipping..."
fi

echo ""
echo "[3/6] Running Trivy (Container Vulnerability Scanner)..."
if command -v trivy &> /dev/null; then
    mkdir -p security-reports
    trivy fs . --format json --output security-reports/trivy-fs-report.json --severity CRITICAL,HIGH || true
    echo "✓ Trivy filesystem scan completed"
else
    echo "⚠ Trivy not installed, skipping..."
fi

echo ""
echo "[4/6] Checking Dockerfile security..."
if [ -f "Dockerfile" ]; then
    echo "Checking for security best practices in Dockerfile..."
    
    if grep -q "USER " Dockerfile; then
        echo "✓ Non-root user configured"
    else
        echo "✗ Warning: No USER directive found in Dockerfile"
    fi
    
    if grep -q "HEALTHCHECK" Dockerfile; then
        echo "✓ Health check configured"
    else
        echo "✗ Warning: No HEALTHCHECK found in Dockerfile"
    fi
    
    if grep -q "COPY --from=builder" Dockerfile || grep -q "COPY --chown=" Dockerfile; then
        echo "✓ Multi-stage build or proper file ownership configured"
    else
        echo "⚠ Consider using multi-stage builds"
    fi
    
    echo "✓ Dockerfile security check completed"
else
    echo "⚠ Dockerfile not found"
fi

echo ""
echo "[5/6] Checking docker-compose security..."
if [ -f "docker-compose.yml" ]; then
    echo "Checking docker-compose.yml security settings..."
    
    if grep -q "no-new-privileges" docker-compose.yml; then
        echo "✓ no-new-privileges configured"
    else
        echo "✗ Warning: no-new-privileges not configured"
    fi
    
    if grep -q "cap_drop" docker-compose.yml; then
        echo "✓ Capability dropping configured"
    else
        echo "✗ Warning: No capability dropping configured"
    fi
    
    if grep -q "read_only" docker-compose.yml; then
        echo "✓ Read-only filesystem configured"
    else
        echo "⚠ Consider using read-only filesystem"
    fi
    
    echo "✓ docker-compose security check completed"
else
    echo "⚠ docker-compose.yml not found"
fi

echo ""
echo "[6/6] Checking for sensitive data exposure..."
echo "Scanning for potential secrets..."

POTENTIAL_SECRETS=$(grep -r --include="*.py" --include="*.yaml" --include="*.yml" --include="*.json" \
    -E "(password|secret|api_key|token|credential)\s*=\s*['\"][^'\"]+['\"]" \
    --exclude-dir=".git" --exclude-dir="venv" --exclude-dir="__pycache__" \
    . 2>/dev/null | grep -v ".env.example" | grep -v "# " || true)

if [ -z "$POTENTIAL_SECRETS" ]; then
    echo "✓ No hardcoded secrets found"
else
    echo "✗ Warning: Potential hardcoded secrets found:"
    echo "$POTENTIAL_SECRETS"
fi

echo ""
echo "========================================="
echo "Security scan completed!"
echo "Reports saved to: security-reports/"
echo "========================================="
