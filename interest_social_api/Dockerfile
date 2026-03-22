# =============================================================================
# Interest Social API - Production Grade Dockerfile
# Multi-stage build with security hardening
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder Stage
# Purpose: Build Python wheels for faster installation
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

# Build arguments
ARG PYTHON_VERSION=3.11
ARG APP_VERSION=1.0.0

# Security: Run as non-root during build
RUN groupadd --gid 1000 builder && \
    useradd --uid 1000 --gid builder --shell /bin/false builder

# Install build dependencies with minimal footprint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /build

# Copy and install Python dependencies
COPY --chown=builder:builder requirements.txt .

# Create wheels for faster installation in production stage
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Production Stage
# Purpose: Minimal runtime image with security hardening
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS production

# Metadata labels (OCI standard)
LABEL maintainer="SRE Team <sre@company.com>"
LABEL version="1.0.0"
LABEL description="Interest Social API - Production Ready"
LABEL org.opencontainers.image.title="Interest Social API"
LABEL org.opencontainers.image.description="Production-grade Flask API for social platform"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/company/interest-social-api"

# Build arguments
ARG PYTHON_VERSION=3.11
ARG APP_VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF

LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"

# Environment variables for Python and application
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    APP_HOME=/app \
    APP_VERSION=${APP_VERSION} \
    PYTHON_VERSION=${PYTHON_VERSION} \
    GUNICORN_WORKERS=4 \
    GUNICORN_THREADS=2 \
    GUNICORN_BIND_ADDRESS=0.0.0.0 \
    GUNICORN_BIND_PORT=5000 \
    GUNICORN_TIMEOUT=120 \
    GUNICORN_GRACEFUL_TIMEOUT=120 \
    GUNICORN_KEEPALIVE=5 \
    GUNICORN_MAX_REQUESTS=1000 \
    GUNICORN_MAX_REQUESTS_JITTER=50 \
    GUNICORN_WORKER_CLASS=gevent \
    GUNICORN_WORKER_CONNECTIONS=1000 \
    GUNICORN_BACKLOG=2048 \
    GUNICORN_WORKER_TMP_DIR=/dev/shm \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libpq5 \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

# Create non-root user for security
# Using fixed UID/GID for consistency across deployments
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/false --create-home --home-dir /home/appuser appuser

# Set working directory
WORKDIR ${APP_HOME}

# Copy pre-built wheels from builder stage
COPY --from=builder /build/wheels /wheels

# Install Python packages from wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code with proper ownership
COPY --chown=appuser:appgroup . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/tmp /app/data && \
    chown -R appuser:appgroup /app/logs /app/tmp /app/data && \
    chmod 750 /app/logs /app/tmp /app/data && \
    chmod 755 /app/data

# Security: Remove unnecessary tools and files
RUN rm -rf /tmp/* /var/tmp/* && \
    find /usr -name "*.pyc" -delete && \
    find /usr -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE ${GUNICORN_BIND_PORT}

# Health check configuration
# Uses the application's health endpoint
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=40s \
            --retries=3 \
    CMD curl -fsS http://${GUNICORN_BIND_ADDRESS}:${GUNICORN_BIND_PORT}/health > /dev/null || exit 1

# Use SIGTERM for graceful shutdown
STOPSIGNAL SIGTERM

# Set entrypoint and command
ENTRYPOINT ["gunicorn"]
CMD ["--config", "gunicorn.conf.py", "run:app"]

# -----------------------------------------------------------------------------
# Stage 3: Development Stage (optional)
# Purpose: Includes development tools for debugging
# -----------------------------------------------------------------------------
FROM production AS development

USER root

# Install development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim-tiny \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    debugpy==1.8.1 \
    pytest==8.1.0 \
    pytest-cov==4.1.0

USER appuser

# Override command for development
CMD ["--config", "gunicorn.conf.py", "--reload", "run:app"]
