# ────────────────────────────────────────────────────────────────────────────
# Stage 1 – builder
# ────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install OS deps needed for cryptography & mysqlclient wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ────────────────────────────────────────────────────────────────────────────
# Stage 2 – runtime
# ────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Non-root user
RUN useradd -m appuser

COPY --from=builder /install /usr/local
COPY app/ ./app/

USER appuser

EXPOSE 8000

# Health-check for Docker / Kubernetes
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
