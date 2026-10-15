"""Optional local visual QA using the browser package in the Agent venv."""

from playwright.sync_api import sync_playwright

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "http://127.0.0.1:8030/"

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=EDGE, headless=True)
    for width, height in [(1440, 1000), (390, 844)]:
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.goto(URL)
        print(width, page.evaluate("({inner:innerWidth,scroll:document.documentElement.scrollWidth})"))
        print(page.evaluate("""Array.from(document.querySelectorAll('*'))
            .filter(e => e.getBoundingClientRect().right > innerWidth + 1)
            .slice(0, 12)
            .map(e => ({tag: e.tagName, cls: e.className, right: Math.round(e.getBoundingClientRect().right)}))"""))
        page.screenshot(path=f"preview-{width}.png", full_page=True)
        page.close()
    browser.close()
