"""使用本机 Chrome 检查 yugan-agent 控制台的四个主要入口。"""

import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright


async def main():
    chrome = Path(
        os.environ.get("YUGAN_CHROME", "C:/Program Files/Google/Chrome/Application/chrome.exe")
    )
    if not await asyncio.to_thread(chrome.is_file):
        raise SystemExit("找不到 Chrome；可用 YUGAN_CHROME 指定 chrome.exe 路径")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=str(chrome), headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.goto("http://127.0.0.1:8020/", wait_until="networkidle")
            assert "离线演示" in await page.locator("#mode-badge").inner_text()

            await page.locator('[data-view="tools"]').click()
            await page.locator(".tool-card").first.wait_for()
            assert await page.locator(".tool-card").count() >= 7

            await page.locator('[data-view="workflow"]').click()
            await page.locator("#run-workflow").click()
            await page.locator("#workflow-result .stat").first.wait_for()
            assert "completed" in await page.locator("#workflow-result").inner_text()
            assert "3" in await page.locator("#workflow-result").inner_text()
            screenshot = Path("workspace/output/web-smoke.png")
            screenshot.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot), full_page=True)

            await page.locator('[data-view="chat"]').click()
            await page.locator("#prompt").fill("计算 (12 + 8) * 3")
            await page.locator("#send").click()
            await page.locator(".message.assistant").last.wait_for()
            assert "60" in await page.locator(".message.assistant").last.inner_text()

            await page.locator("#prompt").fill('<img src=x onerror="alert(1)">')
            await page.locator("#send").click()
            await page.wait_for_function(
                "document.querySelectorAll('.message.assistant').length >= 2"
            )
            assert await page.locator(".message.user img").count() == 0

            await page.locator('[data-view="context"]').click()
            await page.locator(".session-item").first.wait_for()
            await page.locator(".session-item").first.click()
            await page.locator("#session-detail .detail-row").first.wait_for()
            assert not errors, errors
            print(f"WEB_SMOKE_OK screenshot={await asyncio.to_thread(screenshot.resolve)}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
