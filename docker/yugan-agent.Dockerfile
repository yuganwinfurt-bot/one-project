FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY yugan-agent/pyproject.toml yugan-agent/README.md ./
COPY yugan-agent/src ./src
RUN pip install --no-cache-dir . \
    && mkdir -p /app/workspace /app/.yugan \
    && chown -R 1000:1000 /app

USER 1000:1000
CMD ["python", "-m", "yugan_agent", "serve", "--host", "127.0.0.1", "--port", "8020"]
