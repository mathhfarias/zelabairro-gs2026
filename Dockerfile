FROM python:3.12-slim-trixie
LABEL org.opencontainers.image.source="https://github.com/mathhfarias/zelabairro-gs2026"

# Atualizar zlib1g do Debian antes de instalar a aplicação.
# O Trivy continua bloqueando qualquer CVE HIGH/CRITICAL corrigível.
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends --only-upgrade zlib1g; \
    rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/zelabairro.sqlite3 \
    APP_ENV=production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd -g 10001 appuser \
    && useradd -u 10001 -g appuser -M -s /usr/sbin/nologin appuser \
    && mkdir -p /data \
    && chown appuser:appuser /data
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser wsgi.py ./wsgi.py
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--access-logfile", "-", "wsgi:app"]

# GS 2026.2 - teste final de deploy automatico Render

# GS 2026.2 - teste final de deploy automatico Render
