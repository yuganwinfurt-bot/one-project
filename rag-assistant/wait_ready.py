"""等待本项目的前后端真正就绪后，启动器才打开浏览器。"""
import argparse
import json
import time
import urllib.error
import urllib.request


def wait_for_services(timeout: float = 90) -> int:
    # 本机健康检查不经过系统 HTTP 代理。
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    services = {
        "FastAPI": "http://127.0.0.1:8000/api/health",
        "React": "http://127.0.0.1:4173/",
    }
    pending = dict(services)
    errors = {}
    deadline = time.monotonic() + timeout
    print("等待前后端启动完成...", flush=True)
    while pending and time.monotonic() < deadline:
        for name, url in list(pending.items()):
            try:
                with opener.open(url, timeout=2) as response:
                    body = response.read().decode("utf-8")
                if name == "FastAPI":
                    payload = json.loads(body)
                    if payload.get("status") != "ok" or payload.get("service") != "本地 RAG 知识库助手":
                        raise ValueError("8000 端口被其他服务占用")
                elif "知答" not in body or 'id="root"' not in body:
                    raise ValueError("4173 端口被其他网页占用")
                print(f"{name} 已就绪：{url}", flush=True)
                del pending[name]
            except (OSError, urllib.error.URLError, ValueError) as exc:
                errors[name] = str(exc)
        if pending:
            time.sleep(1)
    if pending:
        for name in pending:
            print(f"{name} 启动超时：{errors.get(name, '未响应')}", flush=True)
        print("请查看对应服务窗口中的错误信息。", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=90)
    raise SystemExit(wait_for_services(parser.parse_args().timeout))
