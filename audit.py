import json, asyncio, sys, time
from pathlib import Path
from tabulate import tabulate
from playwright.async_api import async_playwright

TARGET = sys.argv[1] if len(sys.argv) > 1 else "https://clubtattoo.com"
STAMP = int(time.time())
OUT = Path("output"); OUT.mkdir(exist_ok=True)

AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js"

async def run_audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(TARGET, timeout=60000)
        await asyncio.sleep(3)

        # Screenshot for executive summary
        shot = OUT / f"screenshot-{STAMP}.png"
        await page.screenshot(path=shot, full_page=True)

        # axe scan
        await page.add_script_tag(url=AXE_CDN)
        axe_results = await page.evaluate("async () => await axe.run()")
        violations = axe_results["violations"]

        # --- Markdown report ---
        md_lines = [
            f"# Compliance Audit – {TARGET}",
            f"Generated: <t:{STAMP}:f>",
            "",
            f"**Total accessibility violations:** `{len(violations)}`",
            "",
            "![screenshot](./" + shot.name + ")",
            ""
        ]

        table = []
        for v in violations:
            rule = v["id"]
            impact = v.get("impact", "unknown")
            selector = v["nodes"][0]["target"][0]  # first offending selector
            table.append([rule, impact, selector])

        md_lines.append(tabulate(table,
                                 headers=["Rule", "Impact", "Example selector"],
                                 tablefmt="github"))

        report_file = OUT / f"report-{STAMP}.md"
        report_file.write_text("\n".join(md_lines), encoding="utf-8")

        # Also keep the raw JSON
        (OUT / f"axe-results-{STAMP}.json").write_text(
            json.dumps(axe_results, indent=2), encoding="utf-8")

        print(f"✅ Report saved to {report_file}")
        await browser.close()

asyncio.run(run_audit())
