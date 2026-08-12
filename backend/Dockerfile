# Stage 1: Dependencies
FROM python:3.12-slim AS deps
WORKDIR /app
RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y postgresql-client curl && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash app
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY scripts/ scripts/
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
ENTRYPOINT ["./entrypoint.sh"]
