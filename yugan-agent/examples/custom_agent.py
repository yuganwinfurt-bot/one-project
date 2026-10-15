"""Python API 示例：创建无 Key Agent 并执行计算。"""

import asyncio

from yugan_agent.runtime import create_agent


async def main():
    agent = create_agent()
    try:
        result = await agent.run("计算 (12 + 8) * 3", session_id="python_example")
        print(result.model_dump_json(indent=2))
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
