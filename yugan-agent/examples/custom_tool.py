"""在自己的 Agent 实例上注册土壤湿度转换工具。"""

import asyncio

from yugan_agent import ToolRegistry, tool


@tool
def soil_moisture(raw: int) -> dict:
    """把 0–4095 的 ADC 示例值转换为百分比。"""
    if not 0 <= raw <= 4095:
        raise ValueError("raw 必须在 0–4095 之间")
    return {"percent": round(raw / 4095 * 100, 1)}


async def main():
    registry = ToolRegistry()
    registry.register(soil_moisture)
    result = await registry.execute("soil_moisture", '{"raw":2048}')
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
