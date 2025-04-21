# ---------- audit.py ----------
"""
Run Playwright + axe‑core, save results to ./output/
Creates:
  • axe-results-<ts>.json
  • report-<ts>.md
  • screenshot-<ts>.png
Exits with code 1 on Playwright error or missing URL.
"""

import sys, os, json, asyncio, time
from pathlib import Path
from playwright.async_api import async_playwright, Error as PwError

########################################################################
# Site URL – from env (CI) or first CLI arg
########################################################################
SITE = os.environ.get("SITE_URL") or (sys.argv[1] if len(sys.argv) > 1 else "")
if not SITE.strip():
    sys.exit("❌ No site URL provided to audit.py – dispatch payload missing 'site'")

########################################################################
# Output folder
########################################################################
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

########################################################################
# Main audit routine
########################################################################
async def run_audit(url: str):
    ts = int(time.time())
    axe_json = OUTPUT / f"axe-results-{ts}.json"
    md_file  = OUTPUT / f"report-{ts}.md"
    png_file = OUTPUT / f"screenshot-{ts}.png"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})
            await page.goto(url, timeout=120_000)
            await page.screenshot(path=png_file, full_page=True)

            # inject axe-core and run scan
            await page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.3/axe.min.js")
            results = await page.evaluate("await axe.run()")
            axe_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    except PwError as e:
        print("❌ Playwright error:", e)
        sys.exit(1)

    # minimal markdown report
    md_file.write_text(
        f"# Accessibility Audit for {url}\n\n"
        f"Total violations found: **{len(results['violations'])}**\n", encoding="utf-8"
    )

    print(f"✅ Saved axe results → {axe_json}")
    print(f"✅ Saved Markdown   → {md_file}")
    print(f"✅ Saved screenshot → {png_file}")

########################################################################
# Entrypoint
########################################################################
if __name__ == "__main__":
    asyncio.run(run_audit(SITE))
# --------------------------------
