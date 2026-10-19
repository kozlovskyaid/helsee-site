#!/usr/bin/env python3
"""Builds privacy.html and terms.html from the app's own LegalTexts.swift.

The site, the embedded texts and the App Privacy answers must agree; copying
by hand is how they stop agreeing. Run after every change to LegalTexts:

    python3 build_legal.py ../healthporter/Helsee/Settings/LegalTexts.swift
"""
import html, re, sys
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "../healthporter/Helsee/Settings/LegalTexts.swift").read_text()
updated = re.search(r'lastUpdated = "([^"]+)"', src).group(1)

def sections(name):
    block = src[src.index(f"static let {name}"):]
    block = block[:block.index("\n    ]\n")]
    out = []
    for title, body in re.findall(r'title: "([^"]+)",\s*body: """\n(.*?)\n\s*"""', block, re.S):
        body = body.replace("\\(lastUpdated)", updated)
        paras = [re.sub(r"\s*\n\s*", " ", p.strip()) for p in re.split(r"\n\s*\n", body) if p.strip()]
        out.append((title, paras))
    return out

def render(paras):
    parts, bullets = [], []
    for p in paras:
        if p.startswith("• "):
            bullets.append(f"<li>{html.escape(p[2:])}</li>")
            continue
        if bullets:
            parts.append("<ul>" + "".join(bullets) + "</ul>"); bullets = []
        parts.append(f"<p>{html.escape(p)}</p>")
    if bullets: parts.append("<ul>" + "".join(bullets) + "</ul>")
    return "\n".join(parts)

page = Path("_page.html").read_text()
for name, file, title in [("privacy", "privacy.html", "Privacy Policy"), ("termsOfUse", "terms.html", "Terms of Use")]:
    key = "privacyPolicy" if name == "privacy" else name
    body = "\n".join(f"<h3>{html.escape(t)}</h3>\n{render(p)}" for t, p in sections(key))
    content = f'<div class="card"><h2>{title}</h2>\n<p class="meta">Last updated: {updated}. This text is the same as the one inside the app.</p>\n{body}\n</div>'
    Path(file).write_text(page.replace("{{TITLE}}", f"{title} — Helsee").replace("{{CONTENT}}", content))
    print("wrote", file)
