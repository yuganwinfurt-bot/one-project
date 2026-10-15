"""调用本机 REST API；先运行 python -m yugan_agent serve。"""

import httpx


def main():
    response = httpx.post(
        "http://127.0.0.1:8020/api/chat",
        json={"prompt": "分析传感器温度", "session_id": "api_example"},
        timeout=60,
    )
    response.raise_for_status()
    print(response.json()["answer"])


if __name__ == "__main__":
    main()
