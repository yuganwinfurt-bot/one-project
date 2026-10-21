FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY customer-service-system/customer-service-system/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY customer-service-system/customer-service-system/backend/app ./app
RUN mkdir -p /app/data /app/uploads && chown -R 1000:1000 /app

USER 1000:1000
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001", "--proxy-headers", "--forwarded-allow-ips=127.0.0.1"]
