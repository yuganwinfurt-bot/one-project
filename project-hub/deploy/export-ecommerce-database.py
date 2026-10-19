"""Export the current local MySQL database without printing its credentials.

Run with the ecommerce backend's virtualenv Python. Does not seed or modify data.
The private output contains account hashes and business data; never commit it.
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
BACKEND = REPO / "customer-service-system" / "customer-service-system" / "backend"
sys.path.insert(0, str(BACKEND))

from app.config import settings  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402


def main():
    url = make_url(settings.DATABASE_URL)
    if not url.drivername.startswith("mysql") or not url.database:
        raise SystemExit("Expected a configured MySQL database.")
    executable = shutil.which("mysqldump")
    if not executable:
        candidate = Path(r"D:\MySQL\MySQL Server 8.0\bin\mysqldump.exe")
        executable = str(candidate) if candidate.is_file() else None
    if not executable:
        raise SystemExit("mysqldump was not found. Add the MySQL bin directory to PATH.")
    output = REPO / "release-output" / "ecommerce-data.sql"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit(f"Output already exists; move it before exporting again: {output}")
    environment = os.environ.copy()
    environment["MYSQL_PWD"] = url.password or ""
    args = [
        executable,
        f"--host={url.host or '127.0.0.1'}",
        f"--port={url.port or 3306}",
        f"--user={url.username or 'root'}",
        "--single-transaction",
        "--skip-lock-tables",
        "--set-gtid-purged=OFF",
        "--no-tablespaces",
        "--hex-blob",
        "--default-character-set=utf8mb4",
        f"--result-file={output}",
        url.database,
    ]
    completed = subprocess.run(args, env=environment)
    if completed.returncode:
        if output.exists():
            output.unlink()
        raise SystemExit(completed.returncode)
    print(f"Exported to: {output}")
    print("Contains private application data. Upload privately; do not commit to Git.")


if __name__ == "__main__":
    main()
