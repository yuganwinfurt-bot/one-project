FROM node:22-bookworm-slim AS frontend-build

WORKDIR /src
COPY project-hub/package.json project-hub/package-lock.json ./project-hub/
COPY rag-assistant/frontend/package.json rag-assistant/frontend/package-lock.json ./rag-assistant/frontend/
COPY customer-service-system/customer-service-system/frontend/package.json customer-service-system/customer-service-system/frontend/package-lock.json ./customer-service-system/customer-service-system/frontend/
RUN npm ci --prefix project-hub \
    && npm ci --prefix rag-assistant/frontend \
    && npm ci --prefix customer-service-system/customer-service-system/frontend

COPY project-hub ./project-hub
COPY rag-assistant/frontend ./rag-assistant/frontend
COPY yugan-agent/src/yugan_agent/web ./yugan-agent/src/yugan_agent/web
COPY customer-service-system/customer-service-system/frontend ./customer-service-system/customer-service-system/frontend
RUN npm --prefix project-hub run build:shared-ui \
    && npm --prefix project-hub run build \
    && npm --prefix rag-assistant/frontend run build \
    && npm --prefix customer-service-system/customer-service-system/frontend run build -- --base=/ecommerce/

FROM python:3.11-slim AS project-hub
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY project-hub/deploy/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY project-hub/hub_api.py ./hub_api.py
COPY --from=frontend-build /src/project-hub/dist ./dist
CMD ["sh", "-c", "uvicorn hub_api:app --host 127.0.0.1 --port \"${HUB_PORT:-8031}\" --proxy-headers --forwarded-allow-ips=127.0.0.1"]

FROM nginx:stable-alpine AS web-gateway
COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=frontend-build /src/rag-assistant/frontend/dist /usr/share/nginx/html/rag
COPY --from=frontend-build /src/customer-service-system/customer-service-system/frontend/dist /usr/share/nginx/html/ecommerce
