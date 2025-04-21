import sys, json, re, subprocess
from pathlib import Path
import markdown
from rule_info import RULE_INFO          # NEW – plain + legal text look‑ups

# ---------- config ----------
CSS = Path("template.css").read_text(encoding="utf-8")

MONEY_BY_SEVERITY = {
    "critical": 6000,
    "serious":  3000,
    "moderate": 1000,
    "minor":     500
}
# -----------------------------

def dollar(x): return "${:,.0f}".format(x)

def impact_class(impact):
    return impact if impact in ("minor", "moderate", "serious", "critical") else "minor"

def main():
    if len(sys.argv) < 2:
        print("Usage: python make_pdf.py <report.md>")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print("❌ Markdown file not found")
        sys.exit(1)

    # -------- parse markdown --------
    md_text = md_path.read_text(encoding="utf-8")

    url_match = re.search(r"https?://[^\s)]+", md_text)
    site_url  = url_match.group(0) if url_match else "site"

    img_match = re.search(r"\!\[.*\]\(\./([^)]+\.png)\)", md_text)
    screenshot = img_match.group(1) if img_match else None

    # -------- load axe results --------
    axe_json = md_path.with_name(md_path.name.replace("report-", "axe-results-")).with_suffix(".json")
    viol = json.loads(axe_json.read_text(encoding="utf-8"))["violations"]

    risk_val = sum(MONEY_BY_SEVERITY.get(v.get("impact","minor"),500) for v in viol)

    # -------- build violations table --------
    rows = []
    for v in viol:
        rule   = v["id"]
        impact = v.get("impact", "minor")
        badge  = f'<span class="badge {impact_class(impact)}">{impact}</span>'

        info  = RULE_INFO.get(rule, {})
        plain = info.get("plain", v["description"])
        legal = info.get("legal", "See WCAG 2.1 for details.")

        rows.append(
            f"<tr><td>{rule}</td><td>{badge}</td>"
            f"<td>{plain}</td><td>{legal}</td></tr>"
        )

    viol_table = (
        '<table class="table"><thead><tr>'
        '<th>Rule</th><th>Impact</th><th>Issue</th><th>Legal reference</th>'
        '</tr></thead><tbody>'
        + "".join(rows) +
        '</tbody></table>'
    )

    # -------- assemble HTML --------
    html_parts = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<style>{CSS}</style></head><body>",
        f"<h1>Compliance Risk Report – {site_url}</h1>",
        f"<div class='riskbar'>Estimated exposure: {dollar(risk_val)}</div>"
    ]
    if screenshot:
        html_parts.append(f"<img src='{screenshot}' style='width:100%; margin-bottom:12px;'>")
    html_parts.append(viol_table)
    html_parts.append("</body></html>")

    tmp_html = md_path.with_suffix(".html")
    tmp_html.write_text("".join(html_parts), encoding="utf-8")

    out_pdf = md_path.with_suffix(".pdf")
    subprocess.run([
        "wkhtmltopdf",
        "--enable-local-file-access",
        "-q",
        str(tmp_html),
        str(out_pdf)
    ], check=True)

    print("✅ PDF saved to", out_pdf)

if __name__ == "__main__":
    main()
