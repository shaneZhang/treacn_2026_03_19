FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

FROM python:3.11-slim-bookworm

LABEL maintainer="SRE Team"
LABEL version="1.0.0"
LABEL description="Interest Social API - Production Ready"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_HOME=/app \
    GUNICORN_WORKERS=4 \
    GUNICORN_THREADS=2 \
    GUNICORN_BIND_ADDRESS=0.0.0.0 \
    GUNICORN_BIND_PORT=5000 \
    GUNICORN_TIMEOUT=120 \
    GUNICORN_GRACEFUL_TIMEOUT=120 \
    GUNICORN_KEEPALIVE=5 \
    GUNICORN_MAX_REQUESTS=1000 \
    GUNICORN_MAX_REQUESTS_JITTER=50

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR ${APP_HOME}

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY --chown=appuser:appgroup . .

RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appgroup /app/logs /app/tmp && \
    chmod 750 /app/logs /app/tmp

USER appuser

EXPOSE ${GUNICORN_BIND_PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://${GUNICORN_BIND_ADDRESS}:${GUNICORN_BIND_PORT}/health || exit 1

STOPSIGNAL SIGTERM

ENTRYPOINT ["gunicorn"]
CMD ["--config", "gunicorn.conf.py", "run:app"]
