"""First deployment only: create a new MySQL database and private service config.

Run as ubuntu with the ecommerce virtualenv Python after uploading the SQL file.
Never overwrites an existing backend .env or imports over an existing database.
"""
from pathlib import Path
import os
import secrets
import subprocess

from dotenv import dotenv_values

REPO = Path(__file__).resolve().parents[2]
BACKEND = REPO / "customer-service-system/customer-service-system/backend"
ENV_FILE = BACKEND / ".env"
RAG_ENV = REPO / "rag-assistant/backend/.env"
DUMP = Path("/home/ubuntu/ecommerce-data.sql")
DATABASE = "ecommerce_demo"
DATABASE_USER = "ecom_app"


def set_env_value(text, name, value):
    lines = text.splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(name + "="):
            lines[i] = f"{name}={value}"
            found = True
    if not found:
        lines.append(f"{name}={value}")
    return "\n".join(lines) + "\n"


def main():
    if os.name != "posix" or str(REPO) != "/home/ubuntu/one-project":
        raise SystemExit("Run this on the Ubuntu server in /home/ubuntu/one-project.")
    if ENV_FILE.exists():
        raise SystemExit("backend/.env already exists. Stopped; this script is for the first deployment only.")
    if not DUMP.is_file() or not RAG_ENV.is_file():
        raise SystemExit("Upload /home/ubuntu/ecommerce-data.sql and ensure the existing RAG .env is present.")
    existing = subprocess.check_output(
        ["sudo", "mysql", "-NBe", f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{DATABASE}'"],
        text=True,
    ).strip()
    if existing:
        raise SystemExit(f"Database {DATABASE} already exists. Stopped without importing.")
    existing_user = subprocess.check_output(
        ["sudo", "mysql", "-NBe", f"SELECT User FROM mysql.user WHERE User='{DATABASE_USER}' AND Host='127.0.0.1'"],
        text=True,
    ).strip()
    if existing_user:
        raise SystemExit(f"MySQL user {DATABASE_USER} already exists. Stopped without changing it.")
    rag_values = dotenv_values(RAG_ENV)
    sync_token = rag_values.get("ECOM_RAG_SYNC_TOKEN", "") or secrets.token_hex(32)
    if sync_token == "replace-with-a-long-random-token":
        sync_token = secrets.token_hex(32)
    password = secrets.token_hex(24)
    sql = (
        f"CREATE DATABASE {DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
        f"CREATE USER '{DATABASE_USER}'@'127.0.0.1' IDENTIFIED BY '{password}';\n"
        f"GRANT ALL PRIVILEGES ON {DATABASE}.* TO '{DATABASE_USER}'@'127.0.0.1';\n"
    )
    subprocess.run(["sudo", "mysql"], input=sql, text=True, check=True)
    with DUMP.open("rb") as stream:
        subprocess.run(["sudo", "mysql", "--default-character-set=utf8mb4", DATABASE], stdin=stream, check=True)
    config = {
        "DATABASE_URL": f"mysql+pymysql://{DATABASE_USER}:{password}@127.0.0.1:3306/{DATABASE}",
        "JWT_SECRET_KEY": secrets.token_hex(32),
        "JWT_EXPIRE_HOURS": "24",
        "JWT_ALGORITHM": "HS256",
        "SERVER_AUTH_STATUS_URL": "http://127.0.0.1:8020/api/auth/status",
        "LLM_API_KEY": "",
        "LLM_BASE_URL": "https://api.deepseek.com/v1",
        "LLM_MODEL": "deepseek-chat",
        "LLM_TIMEOUT": "60",
        "LLM_MAX_RETRIES": "0",
        "RAG_BASE_URL": "http://127.0.0.1:8000",
        "RAG_ECOM_KNOWLEDGE_BASE_ID": "ecommerce-analysis-platform",
        "RAG_SYNC_TOKEN": sync_token,
        "RAG_SEARCH_TIMEOUT_SECONDS": "30",
        "RAG_SYNC_TIMEOUT_SECONDS": "600",
    }
    with os.fdopen(os.open(ENV_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as stream:
        stream.write("\n".join(f"{key}={value}" for key, value in config.items()) + "\n")
    rag_text = RAG_ENV.read_text(encoding="utf-8")
    rag_text = set_env_value(rag_text, "ECOM_RAG_SYNC_TOKEN", sync_token)
    origins = {value.strip() for value in (rag_values.get("RAG_WEB_ORIGINS") or "").split(",") if value.strip()}
    origins.add("https://www.yuganwinfurt.top")
    rag_text = set_env_value(rag_text, "RAG_WEB_ORIGINS", ",".join(sorted(origins)))
    RAG_ENV.write_text(rag_text, encoding="utf-8")
    RAG_ENV.chmod(0o600)
    print("Created ecommerce_demo, imported business data and wrote private backend/.env.")
    print("RAG sync token and website Origin are configured. Restart RAG when applying the release.")
    print("Credentials were not printed. Configure the selected chat model in the Agent web settings.")


if __name__ == "__main__":
    main()
