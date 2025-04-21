# ---------- rule_info.py ----------
# Maps axe‑core rule IDs → plain description + legal reference
RULE_INFO = {
    "color-contrast": {
        "plain": "Text and background colours don’t have enough contrast.",
        "legal": "WCAG 2.1 § 1.4.3 (AA) – cited in DOJ settlements."
    },
    "image-alt": {
        "plain": "Images are missing descriptive alt text.",
        "legal": "WCAG 2.1 § 1.1.1 – Gil v. Winn‑Dixie (11th Cir 2021)."
    },
    "label": {
        "plain": "Form control has no programmatic label.",
        "legal": "WCAG 2.1 § 3.3.2 – DOJ 2022 web guidance."
    },
    "link-name": {
        "plain": "Link text is empty or non‑descriptive.",
        "legal": "WCAG 2.1 § 2.4.4 – Target Corp. settlement (2008)."
    },
    "html-has-lang": {
        "plain": "<html> element is missing the lang attribute.",
        "legal": "WCAG 2.1 § 3.1.1 – ADA Title III requirements."
    },
    # …add more high‑frequency rules when convenient…
}
# ----------------------------------
