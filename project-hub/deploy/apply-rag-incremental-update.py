"""核对已拉取的源码与前端包一致后解压；服务重启由命令行下一步执行。"""

import hashlib
import json
import sys
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = "customer-service-system/customer-service-system/frontend/dist"
MANIFEST = "release-output/rag-incremental-sync-manifest.json"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("用法：python3 project-hub/deploy/apply-rag-incremental-update.py 更新包路径")
    archive = Path(sys.argv[1]).expanduser().resolve()
    if not archive.is_file():
        raise SystemExit(f"更新包不存在：{archive}")
    with tarfile.open(archive, "r:gz") as package:
        members = package.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            allowed = member.name == MANIFEST or member.name == FRONTEND or member.name.startswith(FRONTEND + "/")
            if not allowed or path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise SystemExit(f"更新包包含不允许的路径：{member.name}")
            if not (ROOT / member.name).resolve().is_relative_to(ROOT):
                raise SystemExit(f"更新目标超出项目目录：{member.name}")
        stream = package.extractfile(MANIFEST)
        if stream is None:
            raise SystemExit("更新包缺少源码校验清单，请重新生成更新包")
        manifest = json.loads(stream.read().decode("utf-8-sig"))
        if manifest.get("format") != 1 or manifest.get("release") != "rag-incremental-sync":
            raise SystemExit("更新包版本不匹配")
        expected = manifest.get("source_hashes")
        if not isinstance(expected, dict) or not expected:
            raise SystemExit("更新包缺少源码校验值")
        different = []
        for relative, digest in expected.items():
            source = (ROOT / relative).resolve()
            if not source.is_relative_to(ROOT):
                raise SystemExit("源码校验路径超出项目目录")
            if not source.is_file():
                different.append(relative)
                continue
            content = source.read_text(encoding="utf-8-sig").replace("\r\n", "\n").encode("utf-8")
            if hashlib.sha256(content).hexdigest() != digest:
                different.append(relative)
        if different:
            raise SystemExit(
                "源码和页面包版本不一致，未解压页面。\n"
                "请先在电脑提交并推送全部修改，再在服务器 git pull --ff-only origin main。\n"
                + "\n".join(different)
            )
        if FRONTEND + "/index.html" not in {member.name for member in members}:
            raise SystemExit("更新包缺少电商页面入口")
        package.extractall(ROOT, members=members, filter="data")
    print("源码与页面版本一致，增量同步页面已更新。接着重启 rag-assistant 和 ecommerce-api。")


if __name__ == "__main__":
    main()
