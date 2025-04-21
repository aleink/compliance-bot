# ---------- audit.py ----------
import sys, os, json, asyncio
from pathlib import Path
from playwright.async_api import async_playwright

########################################################################
# Fail‑fast guard: refuse to run if no site URL was provided
########################################################################
SITE = os.environ.get("SITE_URL") or (sys.argv[1] if len(sys.argv) > 1 else "")
if not SITE.strip():
    sys.exit("❌ No site URL provided to audit.py – dispatch payload missing 'site'")

########################################################################
# Minimal Playwright scan (unchanged logic below)
########################################################################
REPORT_DIR = Path("output")
REPORT_DIR.mkdir(exist_ok=True)

async def run_audit(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        # … your existing screenshot / axe‑core injection code …
        print("✅ Scan complete")

if __name__ == "__main__":
    asyncio.run(run_audit(SITE))
# --------------------------------
