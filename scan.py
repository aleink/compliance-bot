import json, asyncio, sys, time
from pathlib import Path
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "https://clubtattoo.com"
OUT = Path("output"); OUT.mkdir(exist_ok=True)

AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(TARGET, timeout=60000)
        await asyncio.sleep(3)  # let JS render

        # inject axe-core into the page
        await page.add_script_tag(url=AXE_CDN)
        # run axe inside the browser context
        results = await page.evaluate("async () => await axe.run()")

        ts = int(time.time())
        out_file = OUT / f"axe-results-{ts}.json"
        out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"✅ axe scan complete – {len(results['violations'])} violations saved to {out_file}")

        await browser.close()

asyncio.run(run())
