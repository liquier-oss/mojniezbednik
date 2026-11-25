#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import html
import shutil
import hashlib
import subprocess
from collections import Counter
from datetime import date

BASE_DIR = os.environ.get("HUB_DIR", "/var/www/hub")  # HUB_DIR tylko do testów
DOMAIN = "https://mojniezbednik.pl"
TODAY = date.today().isoformat()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, ".build-state.json")

def _site_updated():
    """Data ostatniej zmiany w repozytorium (commit), a nie dzień uruchomienia generatora."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs"], cwd=SCRIPT_DIR,
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out or TODAY
    except Exception:
        return TODAY

SITE_UPDATED = _site_updated()

# Stan z poprzedniego uruchomienia: skrót treści i data ostatniej realnej zmiany każdej strony
try:
    with open(STATE_FILE, encoding="utf-8") as f:
        BUILD_STATE = json.load(f)
except Exception:
    BUILD_STATE = {}

def pl_plural(n, one, few, many):
    if n == 1:
        return one
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return few
    return many

# 1. Tworzenie katalogów
for sub in ["", "kuchnia", "warsztat", "rower", "listy", "en", "en/workshop", "en/cycling", "en/kitchen", "en/checklists"]:
    os.makedirs(os.path.join(BASE_DIR, sub), exist_ok=True)

def save_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    data = content.strip() + "\n"
    # Data w stopce nie liczy się jako zmiana treści strony
    digest = hashlib.sha256(data.replace(SITE_UPDATED, "").encode("utf-8")).hexdigest()
    prev = BUILD_STATE.get(rel_path, {})
    lastmod = prev.get("lastmod", TODAY) if prev.get("hash") == digest else TODAY
    BUILD_STATE[rel_path] = {"hash": digest, "lastmod": lastmod}
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(data)

# 2. Główny arkusz stylów (Poprawiony selektor * + styl przycisku języka)
STYLE_CSS = """
:root {
    --bg: #0f172a;
    --card: #1e293b;
    --text: #f8fafc;
    --muted: #cbd5e1;
    --accent: #f59e0b;
    --accent-hover: #d97706;
    --border: #334155;
    --success: #10b981;
    --danger: #ef4444;
    --warning-bg: rgba(245, 158, 11, 0.12);
    --danger-bg: rgba(239, 68, 68, 0.12);
    --on-accent: #000;
    --soft: rgba(255,255,255,0.04);
    --soft-2: rgba(255,255,255,0.08);
    --soft-line: rgba(255,255,255,0.06);
    --secondary: #334155;
    --secondary-hover: #475569;
    --shadow: 0 4px 12px rgba(0,0,0,0.35);
    color-scheme: dark;
}
@media (prefers-color-scheme: light) {
    :root {
        --bg: #f8fafc;
        --card: #ffffff;
        --text: #0f172a;
        --muted: #475569;
        --accent: #b45309;
        --accent-hover: #92400e;
        --border: #e2e8f0;
        --success: #047857;
        --danger: #b91c1c;
        --warning-bg: rgba(245, 158, 11, 0.13);
        --danger-bg: rgba(239, 68, 68, 0.09);
        --on-accent: #fff;
        --soft: rgba(15,23,42,0.04);
        --soft-2: rgba(15,23,42,0.08);
        --soft-line: rgba(15,23,42,0.08);
        --secondary: #e2e8f0;
        --secondary-hover: #cbd5e1;
        --shadow: 0 4px 14px rgba(15,23,42,0.10);
        color-scheme: light;
    }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding-bottom: 3rem;
}
a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {
    outline: 3px solid var(--accent);
    outline-offset: 2px;
}
header {
    background: var(--card);
    border-bottom: 1px solid var(--border);
    padding: 1rem;
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-container {
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
}
.logo {
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--accent);
    text-decoration: none;
    letter-spacing: -0.5px;
}
nav { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; }
nav a {
    color: var(--text);
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 0.35rem 0.65rem;
    border-radius: 0.4rem;
    background: var(--soft);
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}
nav a:hover { color: var(--accent); background: var(--soft-2); }
.lang-btn {
    background: transparent;
    color: var(--accent);
    border: 1px solid var(--accent);
    padding: 0.3rem 0.6rem;
    font-size: 0.82rem;
    font-weight: 700;
    border-radius: 0.4rem;
    cursor: pointer;
    margin: 0;
}
.lang-btn:hover { background: var(--accent); color: var(--on-accent); }
a.lang-btn { text-decoration: none; display: inline-block; }
.en-hint {
    max-width: 960px;
    margin: 1rem auto 0;
    padding: 0.6rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    background: var(--warning-bg);
    border: 1px solid var(--accent);
    border-radius: 0.5rem;
}
.en-hint[hidden] { display: none; }
.en-hint a { color: var(--accent); font-weight: 700; text-decoration: none; }
.en-hint-x { background: transparent; border: none; color: var(--muted); font-size: 1.1rem; cursor: pointer; padding: 0 0.25rem; }
main {
    max-width: 960px;
    margin: 1.5rem auto;
    padding: 0 1rem;
}
h1 { font-size: 1.75rem; margin-bottom: 0.75rem; line-height: 1.3; }
h2 { font-size: 1.3rem; margin: 1.5rem 0 0.75rem; color: var(--accent); }
p { margin-bottom: 1rem; color: var(--muted); }
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    padding: 1.25rem;
    text-decoration: none;
    color: var(--text);
    transition: transform 0.15s ease, border-color 0.15s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.card:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
    box-shadow: var(--shadow);
}
.card h3 { font-size: 1.1rem; margin-bottom: 0.5rem; color: var(--text); line-height: 1.35; }
.card .card-val {
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0;
    padding-top: 0.5rem;
    border-top: 1px solid var(--soft-line);
}
.badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 0.2rem 0.5rem;
    border-radius: 0.3rem;
    background: rgba(245, 158, 11, 0.15);
    color: var(--accent);
    margin-bottom: 0.5rem;
    width: fit-content;
}
.param-box {
    background: var(--card);
    border: 2px solid var(--accent);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin: 1.25rem 0;
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 1.25rem;
    text-align: center;
}
.param-item .label { font-size: 0.85rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.25rem; }
.param-item .val { font-size: 1.9rem; font-weight: 800; color: var(--accent); line-height: 1.2; }
.alert-box {
    background: var(--warning-bg);
    border-left: 4px solid var(--accent);
    padding: 1rem 1.25rem;
    border-radius: 0.5rem;
    margin: 1.25rem 0;
    color: var(--text);
    font-size: 0.95rem;
}
.alert-danger {
    background: var(--danger-bg);
    border-left: 4px solid var(--danger);
}
.timer-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    padding: 1.25rem;
    text-align: center;
    margin: 1.5rem 0;
}
.timer-display {
    font-size: 3rem;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    margin: 0.5rem 0;
    color: var(--success);
}
.wakelock-status {
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
button, .btn {
    background: var(--accent);
    color: var(--on-accent);
    border: none;
    padding: 0.65rem 1.1rem;
    font-size: 0.92rem;
    font-weight: 700;
    border-radius: 0.5rem;
    cursor: pointer;
    margin: 0.2rem;
    display: inline-block;
    text-decoration: none;
}
button:hover, .btn:hover { background: var(--accent-hover); }
.btn-secondary { background: var(--secondary); color: var(--text); }
.btn-secondary:hover { background: var(--secondary-hover); }
.filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-bottom: 1rem;
}
.filter-btn {
    background: var(--card);
    color: var(--muted);
    border: 1px solid var(--border);
    padding: 0.45rem 0.85rem;
    font-size: 0.85rem;
    border-radius: 2rem;
    cursor: pointer;
    margin: 0;
}
.filter-btn.active, .filter-btn:hover {
    background: var(--accent);
    color: var(--on-accent);
    border-color: var(--accent);
}
label {
    display: block;
    font-size: 0.92rem;
    font-weight: 600;
    margin-bottom: 0.35rem;
    color: var(--text);
}
input, select {
    width: 100%;
    padding: 0.75rem;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 0.5rem;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.75rem;
}
.info-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    padding: 1.15rem;
    margin-bottom: 0.85rem;
}
.info-box h3 { font-size: 1.05rem; margin-bottom: 0.4rem; color: var(--text); }
.info-box p, .info-box ul { margin-bottom: 0; font-size: 0.95rem; color: var(--muted); }
.info-box ul { padding-left: 1.25rem; }
.info-box li { margin-bottom: 0.35rem; }
.breadcrumbs { font-size: 0.85rem; color: var(--muted); margin-bottom: 1rem; }
.breadcrumbs a { color: var(--accent); text-decoration: none; }
.no-results {
    display: none;
    padding: 1.5rem;
    text-align: center;
    background: var(--card);
    border: 1px dashed var(--border);
    border-radius: 0.5rem;
    color: var(--muted);
    margin-top: 1rem;
}

/* --- IKONY, NAGŁÓWEK I TELEFON --- */
.ico { width: 1.05em; height: 1.05em; flex-shrink: 0; vertical-align: -0.15em; }
.logo { display: inline-flex; align-items: center; gap: 0.4rem; }
.logo .ico { width: 1.25em; height: 1.25em; }
.nav-container .lang-btn { order: 3; }
.cat-card h3 { display: flex; align-items: center; gap: 0.55rem; font-size: 1.2rem; }
.cat-card h3 .ico { width: 1.5rem; height: 1.5rem; color: var(--accent); }
.cat-card p { margin-bottom: 0; }
@media (max-width: 640px) {
    header { position: static; padding: 0.65rem 0.85rem 0.5rem; }
    .nav-container { gap: 0.5rem; }
    .nav-container .lang-btn { order: 1; margin-left: auto; }
    nav {
        order: 2;
        flex-basis: 100%;
        flex-wrap: nowrap;
        overflow-x: auto;
        scrollbar-width: none;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 0.15rem;
    }
    nav::-webkit-scrollbar { display: none; }
    main { margin-top: 1rem; }
    h1 { font-size: 1.45rem; }
    h2 { font-size: 1.2rem; }
    .param-box { padding: 1.1rem; }
    .param-item .val { font-size: 1.6rem; }
    .checklist-action-bar { top: 0.5rem; }
    .en-hint { margin: 0.75rem 0.75rem 0; }
}

/* --- TABELE POWIĄZANYCH POZYCJI --- */
.table-wrap { overflow-x: auto; margin-bottom: 1rem; }
.rel-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; background: var(--card); border: 1px solid var(--border); border-radius: 0.5rem; overflow: hidden; }
.rel-table th { text-align: left; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.4px; color: var(--muted); padding: 0.55rem 0.8rem; border-bottom: 1px solid var(--border); }
.rel-table td { padding: 0.55rem 0.8rem; border-bottom: 1px solid var(--soft-line); vertical-align: top; color: var(--text); }
.rel-table td:last-child { color: var(--accent); font-weight: 700; white-space: nowrap; }
.rel-table tr:last-child td { border-bottom: none; }
.rel-table a { color: var(--text); text-decoration: none; }
.rel-table a:hover { color: var(--accent); text-decoration: underline; }
.rel-table tr.current td { background: var(--warning-bg); font-weight: 700; }
.rel-table tr.current td:first-child { box-shadow: inset 3px 0 0 var(--accent); }
@media (max-width: 640px) { .rel-table td:last-child { white-space: normal; } }

/* --- STYLE DLA INTERAKTYWNYCH CHECKLIST --- */
.checklist-action-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1.25rem 0;
    padding: 1rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 68px;
    z-index: 90;
    box-shadow: var(--shadow);
}
.progress-wrap {
    width: 100%;
    background: var(--bg);
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 0.4rem;
}
.progress-bar {
    height: 100%;
    background: var(--success);
    width: 0%;
    transition: width 0.2s ease;
}
.checklist-group { margin-bottom: 1.5rem; }
.group-title {
    color: var(--accent);
    font-size: 1.15rem;
    font-weight: 700;
    margin: 1.25rem 0 0.5rem;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid var(--border);
}
.item-list { list-style: none; padding: 0; }
.item-row {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    padding: 0.65rem 1rem;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    user-select: none;
    transition: background 0.12s ease;
}
.item-row:hover { border-color: var(--accent); }
.item-row input[type="checkbox"] {
    width: 1.25rem;
    height: 1.25rem;
    margin: 0;
    accent-color: var(--accent);
    cursor: pointer;
    flex-shrink: 0;
}
.item-row.checked span {
    text-decoration: line-through;
    opacity: 0.45;
}
.add-custom-box {
    display: flex;
    gap: 0.5rem;
    margin: 1.25rem 0;
}
.add-custom-box input { margin-bottom: 0; }

footer {
    max-width: 960px;
    margin: 3rem auto 0;
    padding: 1.5rem 1rem 0;
    border-top: 1px solid var(--border);
    font-size: 0.85rem;
    color: var(--muted);
}
.footer-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}
.footer-grid h4 { color: var(--text); margin-bottom: 0.5rem; font-size: 0.95rem; }

@media print {
    body { background: #fff !important; color: #000 !important; font-size: 10.5pt; padding: 0; line-height: 1.35; }
    header, footer, .checklist-action-bar, .add-custom-box, .breadcrumbs, .btn, button, .alert-box, .rel-table, .table-wrap { display: none !important; }
    main { max-width: 100%; margin: 0; padding: 0; }
    h1 { font-size: 15pt; margin-bottom: 0.25rem; color: #000 !important; }
    h2, .group-title { color: #000 !important; border-bottom: 1px solid #999; font-size: 11.5pt; margin: 0.75rem 0 0.25rem; }
    p { color: #333 !important; margin-bottom: 0.4rem; font-size: 9.5pt; }
    .item-row {
        background: transparent !important;
        border: none !important;
        border-bottom: 1px dotted #ccc !important;
        border-radius: 0;
        padding: 0.22rem 0;
        margin: 0;
        color: #000 !important;
        page-break-inside: avoid;
    }
    .item-row.checked span { text-decoration: none; opacity: 1; }
}
"""
save_file("style.css", STYLE_CSS)
# Wersja arkusza w adresie: każda zmiana stylów wymusza pobranie nowego pliku (omija pamięć podręczną)
STYLE_VER = hashlib.sha256(STYLE_CSS.encode("utf-8")).hexdigest()[:10]

# Ikony SVG (proste, własne); dziedziczą kolor tekstu (currentColor)
def _svg(inner, sw=2):
    return (f'<svg class="ico" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>')
ICON = {
    "bolt": '<svg class="ico" width="1em" height="1em" viewBox="0 0 64 64" aria-hidden="true"><path d="M38 6 16 36h14l-4 22 22-30H34z" fill="currentColor"/></svg>',
    "kitchen": _svg('<path d="M4 10h16v3a6 6 0 0 1-6 6h-4a6 6 0 0 1-6-6z"/><path d="M2 10h2M20 10h2"/><path d="M9 6c0-1 1-1 1-2M14 6c0-1 1-1 1-2"/>'),
    "workshop": _svg('<path d="M14.7 6.3a4 4 0 0 0 5 5l-9.4 9.4a2.1 2.1 0 0 1-3-3z"/><path d="M14.7 6.3 17 4l3 3-2.3 2.3"/>'),
    "bike": _svg('<circle cx="5.5" cy="16.5" r="3.5"/><circle cx="18.5" cy="16.5" r="3.5"/><path d="M5.5 16.5 9 9h6l3.5 7.5M9 9l3 7.5h-6.5M15 9l-1.5-3H11"/>'),
    "lists": _svg('<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="m9 12 2 2 4-4M9 17h6"/>'),
}

def related_table(rows, current_href, heading, col1, col2):
    """Tabela pozycji z tej samej kategorii; bieżąca strona wyróżniona i bez linku."""
    if len(rows) < 2:
        return ""
    trs = []
    for href, label, value in rows:
        if href == current_href:
            trs.append(f'<tr class="current" aria-current="page"><td>{label}</td><td>{value}</td></tr>')
        else:
            trs.append(f'<tr><td><a href="{href}">{label}</a></td><td>{value}</td></tr>')
    return (f'<h2>{heading}</h2>\n    <div class="table-wrap"><table class="rel-table">'
            f'<thead><tr><th>{col1}</th><th>{col2}</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div>')

def _is_meat(slug):
    return any(k in slug for k in ["kurczak", "udka", "skrzydelka", "nuggetsy", "karkowka", "schabowy", "mielone", "stek", "burger", "losos", "dorsz", "krewetki", "paluszki", "boczek", "kielbasa"])

def _badge_group(badge):
    return badge.split(" ", 1)[-1]

# 3. Wspólny szablon HTML. Wersja PL i EN (My Toolbelt) to osobne strony:
#    polska pod "/", angielska pod "/en/", powiązane przez hreflang.
ALT_PL2EN = {}   # wypełniane przed generowaniem stron (sekcja 4b)
ALT_EN2PL = {}

def wrap_html(title, desc, body, canonical_path="", noindex=False, lang="pl"):
    canonical_url = f"{DOMAIN}/{canonical_path}"   # katalogi z "/" na końcu, tak jak w sitemap.xml
    t_attr = html.escape(title, quote=True)
    d_attr = html.escape(desc, quote=True)
    alt_path = (ALT_EN2PL if lang == "en" else ALT_PL2EN).get(canonical_path)
    if noindex:
        head_index = '<meta name="robots" content="noindex">'
        og_url = f"{DOMAIN}/en/" if lang == "en" else f"{DOMAIN}/"
    else:
        head_index = f'<link rel="canonical" href="{canonical_url}">'
        og_url = canonical_url
    hreflang = ""
    if alt_path is not None and not noindex:
        pl_url = canonical_url if lang == "pl" else f"{DOMAIN}/{alt_path}"
        en_url = canonical_url if lang == "en" else f"{DOMAIN}/{alt_path}"
        hreflang = (f'\n    <link rel="alternate" hreflang="pl" href="{pl_url}">'
                    f'\n    <link rel="alternate" hreflang="en" href="{en_url}">'
                    f'\n    <link rel="alternate" hreflang="x-default" href="{pl_url}">')
    if alt_path is not None:
        switch_href = "/" + alt_path
    else:
        switch_href = "/en/" if lang == "pl" else "/"

    if lang == "en":
        title_suffix = "My Toolbelt (MójNiezbędnik.pl)"
        og_locale = "en_GB"
        site_name = "My Toolbelt (MójNiezbędnik.pl)"
        header_html = f"""<header>
    <div class="nav-container">
        <a href="/en/" class="logo" id="siteLogo">{ICON['bolt']}My Toolbelt</a>
        <nav aria-label="Main navigation">
            <a href="/en/kitchen/">{ICON['kitchen']}Kitchen ({N_KUCH_EN})</a>
            <a href="/en/workshop/">{ICON['workshop']}Workshop ({N_WARS_EN})</a>
            <a href="/en/cycling/">{ICON['bike']}Cycling ({N_ROW_EN})</a>
            <a href="/en/checklists/">{ICON['lists']}Checklists ({N_LIST_EN})</a>
        </nav>
        <a class="lang-btn" href="{switch_href}" hreflang="pl" lang="pl" title="Wersja polska">🇵🇱 PL</a>
    </div>
</header>"""
        footer_html = f"""<footer>
    <div class="footer-grid">
        <div>
            <h4>About My Toolbelt</h4>
            <p>A no-fluff collection of practical workshop and cycling tables, calculators, air fryer times and printable checklists. Last updated: <strong>{SITE_UPDATED}</strong>.</p>
        </div>
        <div>
            <h4>Methodology &amp; safety</h4>
            <p>All values are starting reference points. Always check the manufacturer's documentation and your local codes and standards before doing the work.</p>
        </div>
        <div>
            <h4>Contact &amp; feedback</h4>
            <p>Found a mistake or want to suggest a new tool? Email: <a href="mailto:kontakt@mojniezbednik.pl" style="color:var(--accent);">kontakt@mojniezbednik.pl</a></p>
        </div>
    </div>
    <p style="text-align:center; border-top:1px solid var(--border); padding-top:1rem;">© {SITE_UPDATED[:4]} My Toolbelt (MójNiezbędnik.pl) – No tracking cookies. Your settings stay on your device. <a href="/" hreflang="pl" lang="pl" style="color:var(--accent);">Wersja polska</a></p>
</footer>"""
        en_hint = ""
        en_hint_script = ""
    else:
        title_suffix = "Mój Niezbędnik / My Toolbelt"
        og_locale = "pl_PL"
        site_name = "MójNiezbędnik.pl"
        header_html = f"""<header>
    <div class="nav-container">
        <a href="/" class="logo" id="siteLogo">{ICON['bolt']}MójNiezbędnik.pl</a>
        <nav aria-label="Główna nawigacja">
            <a href="/kuchnia/">{ICON['kitchen']}Kuchnia ({N_KUCH})</a>
            <a href="/warsztat/">{ICON['workshop']}Warsztat ({N_WARS})</a>
            <a href="/rower/">{ICON['bike']}Rower ({N_ROW})</a>
            <a href="/listy/">{ICON['lists']}Listy ({N_LIST})</a>
        </nav>
        <a class="lang-btn" href="{switch_href}" hreflang="en" lang="en" title="English version">🇬🇧 EN</a>
    </div>
</header>"""
        footer_html = f"""<footer>
    <div class="footer-grid">
        <div>
            <h4>O projekcie MójNiezbędnik.pl</h4>
            <p>Zbiór praktycznych tabel, punktów startowych, kalkulatorów oraz interaktywnych list pakowania (checklist). Ostatnia aktualizacja: <strong>{SITE_UPDATED}</strong>.</p>
        </div>
        <div>
            <h4>Metodologia i bezpieczeństwo</h4>
            <p>Podane wartości mają charakter orientacyjny (punkty wyjścia). Przed wykonaniem prac elektrycznych, obróbki cieplnej czy montażu komponentów rowerowych zawsze sprawdź dokumentację producenta i normy branżowe.</p>
        </div>
        <div>
            <h4>Kontakt i zgłaszanie uwag</h4>
            <p><span>Znalazłeś błąd w tabeli lub chcesz zasugerować nową listę? Napisz:</span> <a href="mailto:kontakt@mojniezbednik.pl" style="color:var(--accent);">kontakt@mojniezbednik.pl</a></p>
        </div>
    </div>
    <p style="text-align:center; border-top:1px solid var(--border); padding-top:1rem;">© {SITE_UPDATED[:4]} MójNiezbędnik.pl (My Toolbelt) – Brak ciasteczek śledzących. Zaznaczenia list zapisywane są lokalnie na Twoim urządzeniu.</p>
</footer>"""
        hint_txt = "This page is also available in English" if alt_path is not None else "MójNiezbędnik is also available in English (My Toolbelt)"
        en_hint = f"""<div class="en-hint" id="enHint" hidden><a href="{switch_href}" hreflang="en" lang="en">🇬🇧 {hint_txt} →</a><button type="button" class="en-hint-x" aria-label="Close" onclick="document.getElementById('enHint').hidden=true;try{{localStorage.setItem('mn_hide_en','1')}}catch(e){{}}">✕</button></div>
"""
        en_hint_script = """try {
    if (!localStorage.getItem('mn_hide_en') && /^en\\b/i.test(navigator.language || '')) {
        document.getElementById('enHint').hidden = false;
    }
} catch (e) {}
"""

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {title_suffix}</title>
    <meta name="description" content="{d_attr}">
    {head_index}{hreflang}
    <link rel="stylesheet" href="/style.css?v={STYLE_VER}">
    <link rel="icon" href="/favicon.ico" sizes="32x32">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <meta name="theme-color" content="#1e293b" media="(prefers-color-scheme: dark)">
    <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="{site_name}">
    <meta property="og:locale" content="{og_locale}">
    <meta property="og:title" content="{t_attr}">
    <meta property="og:description" content="{d_attr}">
    <meta property="og:url" content="{og_url}">
    <meta property="og:image" content="{DOMAIN}/og.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <script>
    const currentLang = "{lang}";
    function normStr(s) {{
        return (s || "").toLowerCase()
            .normalize("NFD").replace(/[\\u0300-\\u036f]/g, "")
            .replace(/ł/g, "l")
            .replace(/[-_\\s]+/g, "");
    }}
    </script>
</head>
<body>
{header_html}
{en_hint}<main>
{body}
</main>
{footer_html}
<script>
{en_hint_script}</script>
</body>
</html>"""

# 4. Baza danych: Kuchnia, Warsztat (+ 2 kalkulatory), Rower, Listy – liczniki liczone automatycznie (N_*)
KUCHNIA_ITEMS = [
    ("frytki-mrozone", "Frytki mrożone w Airfryerze", 200, 16, "Porcja ok. 300–400 g (jedna warstwa, bez rozmrażania). Potrząśnij koszem w połowie czasu (po 8 min). Czas zależy od grubości frytek (cienkie 12–14 min, grube stekowe do 18 min)."),
    ("frytki-domowe", "Frytki z surowych ziemniaków w Airfryerze", 195, 22, "Słupki ok. 1x1 cm, porcja 350 g. Namocz pokrojone ziemniaki w zimnej wodzie przez 20 minut, dokładnie osusz ręcznikiem papierowym i wymieszaj z 1 łyżką oleju."),
    ("piers-z-kurczaka", "Pierś z kurczaka (filet) w Airfryerze", 190, 14, "Czas orientacyjny dla pojedynczego surowego filetu (ok. 180–220 g, grubość ok. 2–2.5 cm). Kryterium bezpieczeństwa: przed podaniem zmierz temperaturę w najgrubszym miejscu termometrem – musi osiągnąć minimum 74°C."),
    ("udka-z-kurczaka", "Udka i pałki z kurczaka w Airfryerze", 195, 25, "Surowe pałki lub podudzia z kością (ok. 400–500 g). Ułóż skórką do góry i obróć w 15. minucie. Bezpieczna temperatura wewnętrzna przy kości mierzona termometrem to minimum 75–77°C."),
    ("skrzydelka-z-kurczaka", "Chrupiące skrzydełka z kurczaka w Airfryerze", 200, 20, "Surowe skrzydełka ułożone w jednej warstwie (ok. 500 g). Przewróć po 10 minutach. Sprawdź gotowość termometrem (minimum 74°C wewnątrz przy kości)."),
    ("nuggetsy-mrozone", "Nuggetsy z kurczaka (mrożone) w Airfryerze", 200, 10, "Produkt głęboko mrożony, ułożony w pojedynczej warstwie. Przewróć po 5 minutach. Wewnątrz muszą być gorące (min. 74°C)."),
    ("losos-filet", "Filet z łososia (świeży) w Airfryerze", 190, 9, "Surowy filet ze skórą (ok. 150–200 g, grubość 2.5 cm). Piecz skórką do dołu. Dla stopnia średnio wypieczonego wewnętrzna temperatura powinna wynieść ok. 55–60°C (pełne ścięcie białka: 63°C)."),
    ("dorsz-filet", "Dorsz (świeży lub rozmrożony) w Airfryerze", 185, 11, "Rozmrożony i dokładnie osuszony ręcznikiem papierowym filet (ok. 150–180 g). Ryba jest gotowa, gdy mięso łatwo dzieli się na płatki pod widelcem (min. 63°C wewnątrz)."),
    ("paluszki-rybne", "Paluszki rybne mrożone w Airfryerze", 200, 9, "Produkt mrożony (nie rozmrażaj wcześniej). Ułóż z zachowaniem odstępów i przewróć na drugą stronę po 5 minutach."),
    ("krewetki", "Krewetki surowe lub mrożone w Airfryerze", 195, 7, "Rozdziel warianty: krewetki surowe (chłodzone, obrane) piecz 6–7 minut; krewetki mrożone (bez glazury lodowej) potrzebują 8–10 minut. Są gotowe, gdy zmienią kolor na różowy i ułożą się w kształt litery C."),
    ("kielbasa-slaska", "Kiełbasa z Airfryera (jak z grilla)", 190, 10, "Kiełbasa parzona z lodówki (2–3 sztuki). Natnij skórkę w kratkę przed włożeniem i obróć w połowie czasu."),
    ("boczek-plastry", "Chrupiący boczek (bekon) w plastrach z Airfryera", 200, 8, "Cienkie plastry (2–3 mm) ułożone płasko na kratce. Na dno szuflady pod kratką możesz wlać łyżkę wody, aby wytapiający się tłuszcz nie dymił."),
    ("karkowka-plastry", "Karkówka w plastrach z Airfryera", 190, 15, "Surowe plastry o grubości ok. 1.5 cm. Zamarynuj mięso wcześniej i przewróć plastry w 8. minucie (temperatura wewnętrzna min. 65–70°C)."),
    ("schabowy-panierowany", "Kotlet schabowy w panierce z Airfryera", 195, 12, "Rozbity kotlet surowy w tradycyjnej panierce. Spryskaj obie strony mgiełką oleju przed pieczeniem, aby bułka tarta nie pozostała sucha."),
    ("kotlety-mielone", "Kotlety mielone w Airfryerze", 190, 14, "Surowe uformowane kotlety (ok. 80–100 g sztuka, lekko spłaszczone). Przed podaniem upewnij się, że w środku osiągnęły min. 71°C."),
    ("stek-wolowy", "Stek wołowy (Antrykot / Rostbef) w Airfryerze", 200, 9, "Stek o grubości ok. 2.5 cm wyjęty z lodówki 30 min wcześniej (rozgrzej pusty Airfryer przez 3 minuty). Czas orientacyjny dla Medium Rare (54–57°C na termometrze). Po wyjęciu odczekaj 5 minut."),
    ("burger-wolowy", "Burger wołowy w Airfryerze", 195, 10, "Surowy krążek wołowy (ok. 150 g, grubość 1.5–2 cm). Dla pełnego bezpieczeństwa mięsa mielonego piecz do osiągnięcia 71°C wewnątrz."),
    ("ziemniaki-pieczone-cwiartki", "Ziemniaki w ćwiartkach (łódeczki) z Airfryera", 200, 20, "Surowe ziemniaki pokrojone w równe łódeczki (porcja 400 g), wymieszane z łyżką oliwy i przyprawami. Przemieszaj po 10 minutach."),
    ("ziemniak-w-mundurku", "Cały pieczony ziemniak (Jacket Potato) w Airfryerze", 200, 38, "Średniej wielkości ziemniak (ok. 200–250 g). Nakłuj skórkę widelcem w kilku miejscach i natrzyj odrobiną oleju. Sprawdź miękkość wykałaczką."),
    ("bataty-frytki", "Frytki z batatów w Airfryerze", 190, 15, "Surowe bataty pokrojone w słupki 1 cm. Nie przepełniaj kosza – bataty zawierają więcej cukrów i przypalają się szybciej niż zwykłe ziemniaki."),
    ("brokul-rozyczki", "Brokuł pieczony w Airfryerze", 180, 8, "Świeże różyczki brokuła wymieszane z łyżką oliwy. Wlej 1 łyżkę wody na dno misy pod koszem, aby para zapobiegła przypaleniu końcówek."),
    ("kalafior-pieczony", "Różyczki kalafiora z Airfryera", 190, 12, "Świeże różyczki wielkości ok. 3–4 cm wymieszane z oliwą i kurkumą. Przemieszaj w połowie czasu do uzyskania miękkości al dente."),
    ("pieczarki-cale", "Pieczarki w całości z Airfryera", 190, 10, "Średnie świeże pieczarki (ok. 300 g), umyte, osuszone i wymieszane z łyżeczką masła klarowanego lub oliwy."),
    ("cukinia-plastry", "Cukinia w plastrach z Airfryera", 195, 9, "Plastry o grubości ok. 7–8 mm ułożone luźno. Posól bezpośrednio przed pieczeniem, aby nie puściła zbyt dużo wody wcześniej."),
    ("papryka-pieczona", "Papryka pieczona w paskach z Airfryera", 195, 11, "Świeża papryka pokrojona w szerokie paski, skropiona oliwą. Piecz do lekkiego skarmelizowania brzegów skórki."),
    ("szparagi-zielone", "Zielone szparagi w Airfryerze", 195, 7, "Świeże zielone szparagi ze średniej grubości łodygą (odłam zdrewniałe końcówki i skrop oliwą). Cienkie szparagi są gotowe już po 5–6 minutach."),
    ("brukselka", "Chrupiąca brukselka w połówkach z Airfryera", 190, 13, "Świeża brukselka przekrojona na pół i wymieszana z oliwą. Jeśli używasz mrożonej, wydłuż czas do 16–18 minut."),
    ("kukurydza-kolba", "Kolba kukurydzy z Airfryera", 195, 12, "Surowa, świeża kolba kukurydzy cukrowej posmarowana masłem. Obróć w połowie czasu."),
    ("jajka-na-miekko", "Jajka na miękko z Airfryera (bez wody)", 135, 9, "Jajka rozmiar M wyjęte prosto z lodówki (4–5°C). Dla jajek rozmiaru L wydłuż czas o 1 minutę. Po wyjęciu natychmiast przelej zimną wodą."),
    ("jajka-na-twardo", "Jajka na twardo z Airfryera (bez gotowania w wodzie)", 135, 14, "Jajka rozmiar M/L z lodówki. Po zakończeniu odliczania przełóż od razu do zimnej wody na 3 minuty, aby łatwo obrać skorupkę."),
    ("tofu-kostka", "Chrupiące tofu w kostce z Airfryera", 195, 13, "Tofu naturalne/wędzone odsączone z zalewy, pokrojone w kostkę 2 cm i obtoczone w łyżeczce skrobi ziemniaczanej z sosem sojowym."),
    ("ser-halloumi", "Plastry sera Halloumi w Airfryerze", 195, 8, "Plastry o grubości ok. 1 cm. Nie wymaga dodawania tłuszczu – przewróć po 4 minutach."),
    ("camembert-pieczony", "Pieczony Camembert w całości z Airfryera", 180, 9, "Krążek 120 g z naciętą na krzyż górną skórką. Piecz w małej foremce żaroodpornej lub na papierze do pieczenia, aby ser nie wypłynął przez kratkę."),
    ("zapiekanka-bagietka", "Zapiekanka z pieczarkami i serem w Airfryerze", 185, 8, "Rozdziel warianty: domowa zapiekanka (świeża bagietka) piecze się 6–7 minut w 185°C; zapiekanka głęboko mrożona wymaga 9–11 minut w 180°C."),
    ("pizza-mrozona", "Pizza mrożona vs odgrzewana w Airfryerze", 190, 8, "Rozdziel warianty: mrożona mini-pizza piecze się 8–10 minut w 190°C; odgrzewanie kawałka upieczonej pizzy z poprzedniego dnia zajmuje tylko 3–4 minuty w 180°C."),
    ("krokiety-z-kapusta", "Krokiety lub sajgonki w Airfryerze", 190, 10, "Krokiety chłodzone z lodówki (2–3 sztuki). Posmaruj delikatnie olejem z zewnątrz, aby panierka się zazłociła i nie pękała."),
    ("pierogi-pieczone", "Chrupiące pierogi (ugotowane) w Airfryerze", 190, 9, "Ugotowane i ostudzone pierogi obtoczone w odrobinie roztopionego masła lub oleju przed włożeniem do kosza."),
    ("bulki-do-odpieku", "Bułki do odpieku (kajzerki / bagietki) w Airfryerze", 185, 6, "Bułki wstępnie podpieczone (chłodzone: 5–6 min, mrożone: 7–8 min). Zwilż górę odrobiną wody przed włożeniem.")
]

WARSZTAT_ITEMS = [
    ("wiertlo-pod-gwint-m2", "Jakie wiertło pod gwint M2?", "1.6 mm", "Skok zwykły P = 0.4 mm (ISO DIN 13)", "Wymiar dla gwintu nacinanego (gwintownik skrawający). Używaj oleju i wycofuj gwintownik co pół obrotu.", "gwinty"),
    ("wiertlo-pod-gwint-m2-5", "Jakie wiertło pod gwint M2.5?", "2.05 mm (lub 2.1 mm)", "Skok zwykły P = 0.45 mm (ISO DIN 13)", "Popularny rozmiar w elektronice i blokach grzejnych drukarek 3D. Przy braku wiertła 2.05 mm w domowym warsztacie stosuje się 2.1 mm.", "gwinty"),
    ("wiertlo-pod-gwint-m3", "Jakie wiertło pod gwint M3?", "2.5 mm", "Skok zwykły P = 0.5 mm (ISO DIN 13)", "Wzór dla gwintów nacinanych: d - P (3.0 - 0.5 = 2.5 mm). Pod mosiężne inserty wtapiane na gorąco w druku 3D otwór zależy od producenta wkładki (zwykle 4.0–4.2 mm).", "gwinty"),
    ("wiertlo-pod-gwint-m4", "Jakie wiertło pod gwint M4?", "3.3 mm", "Skok zwykły P = 0.7 mm (ISO DIN 13)", "W twardej stali kwasoodpornej (A2/A4) dopuszcza się użycie wiertła 3.4 mm wraz z pastą do gwintowania, aby uniknąć ukręcenia gwintownika.", "gwinty"),
    ("wiertlo-pod-gwint-m5", "Jakie wiertło pod gwint M5?", "4.2 mm", "Skok zwykły P = 0.8 mm (ISO DIN 13)", "Standardowy gwint koszyków na bidon rowerowy oraz profili konstrukcyjnych V-Slot 2020.", "gwinty"),
    ("wiertlo-pod-gwint-m6", "Jakie wiertło pod gwint M6?", "5.0 mm", "Skok zwykły P = 1.0 mm (ISO DIN 13)", "Dla gwintu drobnozwojowego M6x0.75 zastosuj wiertło 5.2 mm. Pod gwintowniki wygniatające (bezwiórowe) otwór musi być większy (ok. 5.55 mm).", "gwinty"),
    ("wiertlo-pod-gwint-m8", "Jakie wiertło pod gwint M8?", "6.8 mm", "Skok zwykły P = 1.25 mm (ISO DIN 13)", "Dla gwintów drobnozwojowych: M8x1.0 wymaga wiertła 7.0 mm, a M8x0.75 wiertła 7.2 mm. Otwór przelotowy pod samą śrubę M8 (ISO 273, szereg średni) to 9.0 mm.", "gwinty"),
    ("wiertlo-pod-gwint-m10", "Jakie wiertło pod gwint M10?", "8.5 mm", "Skok zwykły P = 1.5 mm (ISO DIN 13)", "Dla gwintu drobnozwojowego M10x1.25 użyj wiertła 8.8 mm, a dla M10x1.0 (np. hak przerzutki rowerowej) wiertła 9.0 mm.", "gwinty"),
    ("wiertlo-pod-gwint-m12", "Jakie wiertło pod gwint M12?", "10.2 mm", "Skok zwykły P = 1.75 mm (ISO DIN 13)", "Dla gwintu drobnozwojowego M12x1.5 zastosuj wiertło 10.5 mm, a dla M12x1.25 wiertło 10.8 mm. Wierć wstępnie mniejszym wiertłem prowadzącym.", "gwinty"),
    ("wiertlo-pod-gwint-m14", "Jakie wiertło pod gwint M14?", "12.0 mm", "Skok zwykły P = 2.0 mm (ISO DIN 13)", "Dla gwintu drobnozwojowego M14x1.5 (śruby kół samochodowych, świece) zastosuj wiertło 12.5 mm.", "gwinty"),
    ("wiertlo-pod-gwint-m16", "Jakie wiertło pod gwint M16?", "14.0 mm", "Skok zwykły P = 2.0 mm (ISO DIN 13)", "Dla gwintu drobnozwojowego M16x1.5 użyj wiertła 14.5 mm. Wymaga wykonania fazki wejściowej 45° i smarowania olejem skrawającym.", "gwinty"),
    ("wiertlo-pod-gwint-m20", "Jakie wiertło pod gwint M20?", "17.5 mm", "Skok zwykły P = 2.5 mm (ISO DIN 13)", "Przy gwintowaniu ręcznym stosuj komplet 3 gwintowników (zdzierak, pośredni, wykańczający). Dla M20x1.5 użyj wiertła 18.5 mm.", "gwinty"),
    ("hartowanie-stali-1-2842-nmv", "Hartowanie stali narzędziowej 1.2842 (NMV / O2 / 90MnCrV8)", "790–820°C (olej)", "Odpuszczanie: 180–200°C (ok. 60–61 HRC)", "Niskostopowa stal narzędziowa do pracy na zimno. Podgrzej olej hartowniczy do ok. 50–60°C przed zanurzeniem i odpuszczaj niezwłocznie po ostygnięciu do ok. 50°C (2x po 1–2h).", "stal"),
    ("hartowanie-stali-1095-c105", "Hartowanie stali węglowej 1095 / C105 (1.1545 / W1)", "790–810°C (szybki olej / woda)", "Odpuszczanie: 190–210°C (ok. 60–62 HRC)", "Płytkohartująca stal węglowa (wymaga bardzo szybkiego chłodzenia w pierwszych sekundach). Świetna do hartowania selektywnego z glinką pod hamon.", "stal"),
    ("hartowanie-stali-50hs-51crv4", "Hartowanie stali sprężynowej 50HS (51CrV4 / 1.8159)", "830–860°C (olej)", "Odpuszczanie: 200–250°C (ok. 56–58 HRC)", "Wysoka udarność i sprężystość – stosowana na duże noże obozowe, maczety i narzędzia narażone na uderzenia.", "stal"),
    ("hartowanie-stali-d2-nc11lv", "Hartowanie stali narzędziowej D2 (NC11LV / 1.2379)", "1010–1040°C (olej / powietrze)", "Odpuszczanie: 200–220°C (ok. 59–61 HRC)", "Stal wysokochromowa (~12% Cr). Wymaga zabezpieczenia przed odwęgleniem (folia hartownicza) i wygrzewania przez 20–30 minut w temperaturze austenityzacji.", "stal"),
    ("hartowanie-stali-440c-n9e", "Hartowanie stali nierdzewnej 440C (N9E / 1.4125 / X105CrMo17)", "1030–1050°C (ciepły olej / sprężone powietrze)", "Odpuszczanie: 160–190°C (ok. 58–59 HRC)", "Martenzytyczna stal nierdzewna (nie mylić ze stalą narzędziową NMV 1.2842!). Wymaga dokładnej kontroli temperatury w piecu i folii ochronnej; wymrażanie redukuje austenit szczątkowy.", "stal"),
    ("hartowanie-stali-80crv2-ncv1", "Hartowanie stali 80CrV2 (NCV1 / 1.2235)", "810–840°C (olej)", "Odpuszczanie: 180–200°C (ok. 59–61 HRC)", "Stal węglowo-chromowo-wanadowa o drobnoziarnistej strukturze i szerokim oknie obróbki cieplnej.", "stal"),
    ("druk-3d-pla-temperatury", "Parametry druku 3D: Filament PLA (punkt startowy)", "Dysza: 200–220°C", "Stół: 55–60°C | Nawiew: 100%", "Wartości startowe: przy standardowych prędkościach (60 mm/s) zacznij od 205°C; przy szybkich drukarkach CoreXY / Input Shaper (200–300 mm/s) podnieś do 215–225°C zgodnie z rolką producenta.", "druk3d"),
    ("druk-3d-petg-temperatury", "Parametry druku 3D: Filament PETG (punkt startowy)", "Dysza: 230–245°C", "Stół: 70–80°C | Nawiew: 30–50%", "Zmniejsz prędkość pierwszej warstwy do 30 mm/s. Na gładkim szkle lub płycie PEI stosuj cienką warstwę separatora (klej), bo PETG może związać się ze stołem na stałe.", "druk3d"),
    ("druk-3d-abs-temperatury", "Parametry druku 3D: Filament ABS (punkt startowy)", "Dysza: 245–260°C", "Stół: 95–105°C | Nawiew: 0–20%", "Wymaga zamkniętej, dogrzanej komory roboczej i wentylacji pomieszczenia (opary styrenu).", "druk3d"),
    ("druk-3d-asa-temperatury", "Parametry druku 3D: Filament ASA – odporny na UV", "Dysza: 250–265°C", "Stół: 95–105°C | Nawiew: 10–25%", "Podobnie jak ABS wymaga osłonięcia od przeciągów (komory), ale wykazuje wysoką odporność na promieniowanie UV i warunki atmosferyczne.", "druk3d"),
    ("druk-3d-tpu-temperatury", "Parametry druku 3D: Filament elastyczny TPU (95A)", "Dysza: 220–230°C", "Stół: 40–60°C | Prędkość: 30–40 mm/s", "Ogranicz retrakcję (ok. 0.5–0.8 mm dla ekstruderów Direct Drive) i wyłącz z-hop, aby zminimalizować nitkowanie i blokowanie radełek.", "druk3d"),
    ("druk-3d-nylon-pa12", "Parametry druku 3D: Filament Nylon (PA12)", "Dysza: 255–275°C", "Stół: 80–100°C | Suszenie: 70°C przez min. 8h", "Silnie higroskopijny materiał – przed drukiem wysusz szpulę i podawaj filament bezpośrednio z aktywnej suszarki.", "druk3d"),
    ("jaki-kabel-do-plyty-indukcyjnej-7kw", "Przewód do płyty indukcyjnej 7.2 kW – dobór i warunki", "Orientacyjnie: 5×2.5 mm² lub 5×4 mm² (400V)", "Dobór zabezpieczenia wg DTR płyty i pomiarów (zwykle B16A 3P)", "Karta informacyjna (nie zastępuje projektu!). Ostateczny przekrój zależy od długości trasy, sposobu ułożenia (w tynku vs w rurze/ociepleniu) oraz dopuszczalnego spadku napięcia.", "elektryka"),
    ("jaki-kabel-do-gniazdek-230v", "Przewód do obwodu gniazd 230V – warunki doboru", "Typowo: 3×2.5 mm² Cu", "Zabezpieczenie dobierane do obciążalności długotrwałej Iz (często B16A)", "Dla długich tras lub przewodów prowadzonych w izolacji cieplnej budynku obciążalność prądowa spada – elektryk może wówczas zalecić przekrój 4 mm² lub obniżenie wartości zabezpieczenia.", "elektryka"),
    ("jaki-kabel-do-oswietlenia-led", "Przewód do obwodu oświetlenia 230V – warunki doboru", "Typowo: 3×1.5 mm² lub 4×1.5 mm² Cu", "Zabezpieczenie: dobierane przez elektryka (np. B6A lub B10A)", "Przy dużej liczbie zasilaczy impulsowych LED uwzględnia się prądy rozruchowe przy doborze charakterystyki wyłącznika nadprądowego.", "elektryka"),
    ("jaki-kabel-do-garazu-warsztatu-sila", "Kabel ziemny do garażu / warsztatu (400V) – warunki doboru", "Dobór zależny od mocy, długości i układu sieci", "Przykładowo YKY 5×4 mm² / 5×6 mm² / 5×10 mm²", "Sam próg odległości (np. 30 m) nie wystarcza do doboru kabla! Należy obliczyć spadek napięcia, sprawdzić warunek samoczynnego wyłączenia zasilania (impedancję pętli zwarcia) oraz uwzględnić przyszłe obciążenia.", "elektryka"),
    ("jaki-kabel-do-piekarnika-elektrycznego", "Obwód do piekarnika elektrycznego (ok. 3.5 kW) – warunki", "Typowo: dedykowany obwód 3×2.5 mm² Cu", "Zabezpieczenie wg instrukcji urządzenia i pomiarów (np. B16A)", "Urządzenia stałe o mocy powyżej 2 kW prowadzi się na wydzielonych obwodach z rozdzielnicy. Zawsze sprawdź wytyczne w instrukcji montażu producenta.", "elektryka"),
    ("jaki-kabel-do-ladowarki-wallbox-11kw", "Obwód do ładowarki Wallbox 11 kW (3×16A) – warunki i RCD", "Dobór wg trasy (często min. 5×4 mm² lub 5×6 mm² Cu)", "Wymagana ochrona przed prądem upływu DC > 6 mA!", "UWAGA: Zapis 'RCD typu A/B' jest błędnym skrótem! Zgodnie z normą PN-HD 60364-7-722 wymagany jest wyłącznik różnicowoprądowy typu B LUB wyłącznik typu A współpracujący z certyfikowanym członem detekcji prądu stałego 6 mA DC.", "elektryka"),
    ("proporcje-mieszanki-paliwowej-1-50", "Mieszanka paliwowa 1:50 (Ile oleju 2T na 5L benzyny?)", "100 ml oleju na 5 L benzyny", "Na 1 litr: 20 ml | Na 2 litry: 40 ml | Na 3 litry: 60 ml", "Proporcja 1:50 (2%) dotyczy zazwyczaj markowych olejów syntetycznych/półsyntetycznych w nowoczesnych pilarkach i kosach. Zawsze nadrzędna jest instrukcja obsługi Twojego silnika.", "przeliczniki"),
    ("proporcje-mieszanki-paliwowej-1-40", "Mieszanka paliwowa 1:40 (Ile oleju 2T na 5L benzyny?)", "125 ml oleju na 5 L benzyny", "Na 1 litr: 25 ml | Na 2 litry: 50 ml | Na 3 litry: 75 ml", "Proporcja 1:40 (2.5%) bywa stosowana w okresie docierania silnika lub przy ciężkiej pracy w wysokich temperaturach, jeśli zaleca to producent.", "przeliczniki"),
    ("proporcje-mieszanki-paliwowej-1-25", "Mieszanka paliwowa 1:25 (Ile oleju 2T na 5L benzyny?)", "200 ml oleju na 5 L benzyny", "Na 1 litr: 40 ml | Na 2 litry: 80 ml | Na 3 litry: 120 ml", "Proporcja 1:25 (4%) wymagana w starszych konstrukcjach dwusuwowych oraz części budżetowych kos i pilarek spalinowych.", "przeliczniki"),
    ("rozmiar-klucza-do-sruby-m6-m8-m10-m12", "Tabela rozmiarów klucza do śrub M6, M8, M10, M12 (DIN vs ISO)", "M6=10mm | M8=13mm", "M10: 17mm (DIN 933) lub 16mm (ISO 4017) | M12: 19mm (DIN) lub 18mm (ISO)", "Zwróć uwagę na normę śruby: nowsza norma ISO 4017 zmniejsza wymiar pod klucz dla M10 (z 17 na 16 mm), M12 (z 19 na 18 mm) oraz M14 (z 22 na 21 mm) względem starszej normy DIN 933.", "przeliczniki"),
    ("przelicznik-momentu-nm-na-kgm", "Przelicznik momentu obrotowego: Nm na kgm (kGm)", "10 Nm ≈ 1.02 kgm", "1 kgm ≈ 9.81 Nm (100 Nm ≈ 10.20 kgm)", "Po zakończeniu pracy kluczem dynamometrycznym sprężynowym ustaw podziałkę na najniższą wartość skali, aby nie odkształcać sprężyny pomiarowej.", "przeliczniki"),
    ("wosk-do-lancucha-proporcje-parafina-ptfe", "Domowy wosk do łańcucha rowerowego: Proporcje i temperatura", "500 g parafiny + 5 g dodatku (PTFE / MoS2 / WS2)", "Temperatura kąpieli: 75–85°C (w wolnowarze lub kąpieli wodnej)", "Nie podgrzewaj parafiny bezpośrednio na otwartym ogniu ani płycie! Kluczem do trwałości jest 100% odtłuszczenie nowego łańcucha z fabrycznego smaru (w benzynie ekstrakcyjnej i alkoholu IPA).", "przeliczniki")
]

ROWER_ITEMS = [
    ("cisnienie-gravel-35c", "Ciśnienie startowe w oponach gravelowych 35c (35-622)", "2.6 – 3.4 bar (dętka)", "Tubeless: 2.2 – 2.9 bar (32–42 PSI)", "Wartości startowe dla masy całkowitej zestawu (kolarz + rower + ekwipunek) w przedziale 80–105 kg. Na tylne koło daj o ok. 0.2 bara więcej niż na przednie.", "opony"),
    ("cisnienie-gravel-38c", "Ciśnienie startowe w oponach gravelowych 38c (38-622)", "2.4 – 3.1 bar (dętka)", "Tubeless: 2.0 – 2.7 bar (29–39 PSI)", "Punkt wyjścia do dalszego dostrojenia w terenie dla masy całkowitej zestawu 80–105 kg.", "opony"),
    ("cisnienie-gravel-40c", "Ciśnienie startowe w oponach gravelowych 40c (40-622)", "2.2 – 2.9 bar (dętka)", "Tubeless: 1.8 – 2.5 bar (26–36 PSI)", "Dla masy całkowitej zestawu (kolarz + rower + ekwipunek) ok. 100–115 kg na trasę mieszaną (50% asfalt, 50% szuter) dobrym punktem startowym z dętką jest ok. 2.5 bar przód i 2.7 bar tył.", "opony"),
    ("cisnienie-gravel-42c", "Ciśnienie startowe w oponach gravelowych 42c (42-622)", "2.0 – 2.7 bar (dętka)", "Tubeless: 1.7 – 2.3 bar (25–33 PSI)", "Zbyt wysokie ciśnienie na szutrze zwiększa opory toczenia i zmęczenie, ponieważ opona odbija się od nierówności zamiast je tłumić.", "opony"),
    ("cisnienie-gravel-45c", "Ciśnienie startowe w oponach gravelowych 45c (45-622)", "1.8 – 2.5 bar (dętka)", "Tubeless: 1.5 – 2.1 bar (22–30 PSI)", "Przy bikepackingu z pełnym obciążeniem (masa całkowita zestawu >115 kg) podnieś ciśnienie w tylnym kole o 0.3–0.4 bara, pilnując limitu na boku opony.", "opony"),
    ("cisnienie-gravel-50c-monstercross", "Ciśnienie startowe w oponach 50c / 29×2.0 (50-622)", "1.6 – 2.2 bar (dętka)", "Tubeless: 1.3 – 1.9 bar (19–28 PSI)", "Na obręczach o szerokości wewnętrznej 23–25 mm opona 50 mm stabilnie pracuje na niskim ciśnieniu na leśnych korzeniach i piachu.", "opony"),
    ("cisnienie-szosa-25c", "Ciśnienie startowe w oponach szosowych 25c (25-622)", "6.0 – 7.2 bar (dętka, obręcz z haczykiem)", "Tubeless (Hooked): 5.0 – 6.0 bar | Hookless: MAX 5.0 bar!", "KRYTYCZNE OGRANICZENIE: Dla obręczy bezrantowych (Hookless) producenci (np. ETRTO, Schwalbe) określają bezwzględny maksymalny limit 5.0 bar (72.5 PSI) niezależnie od wagi kolarza oraz wymóg stosowania opon kompatybilnych z Hookless.", "opony"),
    ("cisnienie-szosa-28c", "Ciśnienie startowe w oponach szosowych 28c (28-622)", "5.0 – 6.2 bar (dętka)", "Tubeless (Hooked): 4.2 – 5.2 bar | Hookless: MAX 5.0 bar!", "Przy obręczach bezrantowych (Hookless) pod żadnym pozorem nie przekraczaj 5.0 bar (72.5 PSI).", "opony"),
    ("cisnienie-szosa-32c-road-plus", "Ciśnienie startowe w oponach szosowych 32c (Road Plus 32-622)", "3.8 – 4.8 bar (dętka)", "Tubeless: 3.2 – 4.1 bar (46–60 PSI)", "Znakomity kompromis na dziurawe asfalty. Pamiętaj o limicie 5.0 bar dla systemów Hookless.", "opony"),
    ("cisnienie-mtb-29x2-1", "Ciśnienie startowe w oponach MTB 29×2.1 (54-622)", "1.8 – 2.3 bar (dętka)", "Tubeless: 1.4 – 1.9 bar (20–28 PSI)", "Wartości wyjściowe dla masy całkowitej zestawu 80–105 kg na szybkie trasy XC i leśne dukty.", "opony"),
    ("cisnienie-mtb-29x2-25", "Ciśnienie startowe w oponach MTB 29×2.25 (57-622)", "1.6 – 2.1 bar (dętka)", "Tubeless: 1.2 – 1.7 bar (18–25 PSI)", "Uniwersalny punkt startowy do jazdy terenowej XC.", "opony"),
    ("cisnienie-mtb-29x2-4", "Ciśnienie startowe w oponach MTB 29×2.4 (61-622)", "1.4 – 1.9 bar (dętka)", "Tubeless: 1.1 – 1.5 bar (16–22 PSI)", "Wymaga odpowiednio szerokiej obręczy (najlepiej 25–30 mm wew.), aby opona nie podwijała się w szybkich zakrętach.", "opony"),
    ("cisnienie-mtb-27-5x2-1", "Ciśnienie startowe w oponach MTB 27.5×2.1 (54-584)", "1.9 – 2.4 bar (dętka, dorosły)", "Dla lżejszego zestawu (55–70 kg z rowerem): 1.5 – 1.8 bar", "Przy lżejszych rowerzystach i młodzieży niższe ciśnienie (1.5–1.8 bar) pozwala oponie pracować na korzeniach zamiast odbijać się jak piłka.", "opony"),
    ("cisnienie-rower-miejski-trekking-42c", "Ciśnienie w rowerze miejskim i trekkingowym (40-622 / 42-622)", "3.0 – 4.0 bar", "44 – 58 PSI (sprawdź zakres min–max na boku opony)", "Przy jeździe z obciążonymi sakwami (masa całkowita zestawu >115 kg) utrzymuj tylne koło bliżej górnej granicy (3.8–4.0 bar).", "opony"),
    ("ile-mleczka-tubeless-gravel-40c", "Ile mleczka uszczelniającego (Tubeless) do opony gravelowej 38c–45c?", "60 – 70 ml na koło (pierwsze zalanie)", "Uzupełnianie co 3–5 miesięcy: 30 – 40 ml", "Przy nowej oponie część mleczka wnika w mikropory ścianki bocznej, dlatego pierwsze zalanie powinno być nieco obfitsze.", "opony"),
    ("ile-mleczka-tubeless-mtb-29", "Ile mleczka uszczelniającego (Tubeless) do opony MTB 29 cali (2.0–2.4)?", "90 – 120 ml na koło (pierwsze zalanie)", "Uzupełnianie co 3–5 miesięcy: 50 ml", "Najwygodniej aplikować strzykawką z wężykiem bezpośrednio przez wentyl Presta po wykręceniu rdzenia zaworu.", "opony"),
    ("tabela-obwodow-kol-licznik-rowerowy", "Tabela obwodów kół do licznika rowerowego (mm): 700×38c, 700×40c, 29×2.0", "700×40c ≈ 2200 mm", "700×38c ≈ 2180 mm | 29×2.0 (50-622) ≈ 2265 mm", "Rzeczywisty obwód zależy od ciśnienia, szerokości wewnętrznej obręczy i ugięcia opony. Dla najwyższej dokładności wykonaj test toczenia (od wentyla do wentyla na podłodze pod obciążeniem).", "opony"),
    ("jaka-szerokosc-opony-do-obreczy-19mm-25mm", "Jaka szerokość opony do obręczy 19 mm, 21 mm i 25 mm (wewnętrzna ETRTO)?", "Obręcz 19 mm: zwykle 28–50 mm", "Obręcz 25 mm: zwykle 42–65 mm (sprawdź tabelę producenta obręczy)", "Zbyt wąska opona na szerokiej obręczy zmienia swój profil i naraża rant na uszkodzenie, a zbyt szeroka na wąskiej obręczy pływa w zakrętach.", "opony"),
    ("momenty-dokrecania-rower-mostek-kierownica", "Orientacyjne momenty dokręcania (Nm): Mostek, kierownica, sztyca, pedały", "Mostek/kierownica (Alu): zwykle 4–5 Nm", "Obejma sztycy: 5–6 Nm | Pedały: 35–40 Nm", "UWAGA: Wartości orientacyjne dla komponentów aluminiowych! Zawsze sprawdzaj nadruk 'MAX Nm' bezpośrednio na części. Dla karbonu często obowiązuje limit 4 Nm oraz wymóg stosowania pasty Carbon Grip.", "serwis"),
    ("momenty-dokrecania-kaseta-tarcze-centerlock", "Orientacyjne momenty dokręcania: Kaseta i tarcze hamulcowe", "Nakrętka kasety / tarczy Centerlock: 40 Nm", "Tarcza na 6 śrub (Torx T25): Shimano 2–4 Nm | SRAM 6,2 Nm", "Moment śrub tarczy zależy od producenta – Shimano podaje 2–4 Nm, SRAM/Avid 6,2 Nm; zawsze sprawdź instrukcję swojej tarczy. Dokręcaj kluczem dynamometrycznym w kolejności gwiazdowej (na krzyż), najlepiej z niebieskim klejem do gwintów.", "serwis"),
    ("zuzycie-lancucha-kiedy-wymienic-05-075", "Kiedy wymienić łańcuch rowerowy? (Przymiar 0.5% vs 0.75%)", "Napędy 10 / 11 / 12-rzędowe: przy 0.5%", "Napędy 8 / 9-rzędowe: przy 0.75%", "Używaj przymiaru trójpunktowego (eliminującego luz rolki, np. Park Tool CC-4 lub Pedro's) – zwykłe dwupunktowe blaszki potrafią zawyżać wynik.", "serwis"),
    ("jakie-klocki-hamulcowe-zywiczne-czy-polmetaliczne", "Klocki hamulcowe do roweru: Żywiczne, półmetaliczne czy metaliczne?", "Gravel / Trail: Półmetaliczne", "Góry / Błoto / Bikepacking: Metaliczne | Szosa / Sucho: Żywiczne", "Przed założeniem klocków półmetalicznych lub metalicznych upewnij się, że Twoja tarcza hamulcowa nie ma wybicia 'Resin Pad Only' (tylko pod klocki żywiczne).", "serwis"),
    ("rozmiar-ramy-gravel-wzrost-175-przekrok-80", "Rozmiar ramy gravelowej na wzrost 175 cm i przekrok 80 cm (punkt wyjścia)", "Orientacyjnie: 52–54 cm (S/M lub M)", "Porównuj parametry Stack i Reach (np. Reach 375–388 mm)", "Rozmiarówki producentów różnią się diametralnie. Przy przekroku 80 cm zwróć uwagę na przekrok ramy (Standover) oraz długość rury podsiodłowej.", "dopasowanie"),
    ("rozmiar-ramy-mtb-wzrost-175", "Rozmiar ramy MTB na wzrost 175 cm i przekrok 80 cm (punkt wyjścia)", "Orientacyjnie: M (17–18 cali)", "Współczesne geo MTB: Reach ok. 435–460 mm", "Przy wyborze rozmiaru uwzględnij długość skoku sztycy regulowanej (dropper post), aby mieściła się w rurze podsiodłowej przy Twoim przekroku.", "dopasowanie"),
    ("jak-ustawic-wysokosc-siodelka-wzor-lemonda", "Jak ustawić wysokość siodełka w rowerze? (Wzór LeMonda jako punkt startowy)", "Przekrok (w boso) × 0.883", "Dla przekroku 80 cm: ~70.6 cm (od środka osi suportu do góry siodła)", "Wzór LeMonda to wyłącznie punkt wyjścia! Skoryguj wysokość o ±3–5 mm w zależności od grubości podeszwy butów, bloków SPD i mobilności.", "dopasowanie"),
    ("kalkulator-ftp-w-kg-kolarstwo", "Jak obliczyć W/kg i strefy mocy FTP (Trenażer / Kolarstwo)?", "W/kg = FTP (W) ÷ Masa ciała kolarza (kg)", "Strefa Z2 (Tlenowa / Endurance wg Coggana): 56% – 75% FTP", "Uwaga: Do wyliczenia wskaźnika wydolnościowego W/kg dzieli się moc FTP przez samą masę ciała kolarza (bez wagi roweru).", "dopasowanie")
]

# 5. Pełne 12 Interaktywnych List i Niezbędników (/listy/)
LISTY_ITEMS = [
    ("oboz-kolonie-dziecko", "Co spakować dziecku na obóz letni i kolonie – Lista do druku", "🎒 Dzieci i Szkoła", "Kompletna checklista dla rodzica przed wyjazdem dziecka na kolonie lub obóz młodzieżowy.", [
        ("📄 Dokumenty i Pieniądze (Do podręcznego plecaka)", [
            "Wypełniona karta kwalifikacyjna uczestnika (jeśli nie oddana wcześniej)",
            "Ważna legitymacja szkolna + dowód osobisty lub paszport (przy wyjazdach zagranicznych / przygranicznych)",
            "Karta EKUZ (przy wyjazdach w UE)",
            "Kieszonkowe w drobnych nominałach (w podpisanej kopercie u wychowawcy lub na karcie przedpłaconej)",
            "Leki przyjmowane na stałe wraz z pisemną instrukcją dawkowania dla pielęgniarki/wychowawcy"
        ]),
        ("👕 Odzież i Bielizna (Na 7–10 dni)", [
            "Bielizna osobista i skarpetki (liczba dni + 2 sztuki zapasu)",
            "Koszulki T-shirt (8–10 sztuk)",
            "Krótkie spodenki / szorty (3–4 pary)",
            "Długie spodnie (dresowe i jeansy / trekkingowe – min. 2 pary)",
            "Ciepła bluza z kapturem lub polar (min. 2 sztuki na chłodne wieczory)",
            "Kurtka przeciwdeszczowa i przeciwwiatrowa (z kapturem)",
            "Piżama (cieplejsza i lżejsza)",
            "Strój kąpielowy / kąpielówki (2 komplety)",
            "Nakrycie głowy od słońca (czapka z daszkiem / kapelusz) – OBOWIĄZKOWE!"
        ]),
        ("👟 Obuwie", [
            "Wygodne, rozchodzone buty sportowe / trekkingowe (2 pary)",
            "Sandały lub lekkie buty letnie",
            "Klapki pod prysznic i na basen/plażę"
        ]),
        ("🧴 Higiena i Zdrowie", [
            "Ręczniki: 1 duży kąpielowy, 1 średni do twarzy, 1 szybkoschnący na plażę",
            "Szczoteczka i pasta do zębów w etui",
            "Żel pod prysznic i szampon (najlepiej 2w1 w mniejszych butelkach)",
            "Krem z filtrem UV (SPF 30 lub 50) + pomadka ochronna",
            "Spray na komary i kleszcze",
            "Grzebień / szczotka do włosów + gumki do włosów",
            "Chusteczki higieniczne i nawilżane"
        ]),
        ("🎒 Akcesoria i Sprzęt", [
            "Mały plecak na wycieczki jednodniowe (ok. 15–20L)",
            "Bidon na wodę lub butelka filtrująca",
            "Okulary przeciwsłoneczne z filtrem UV",
            "Duża reklamówka lub tekstylny worek na brudną bieliznę",
            "Telefon + ładowarka (podpisana!) + powerbank"
        ])
    ]),
    ("zimowisko-narty-ferie", "Lista rzeczy na zimowisko i obóz narciarski / snowboardowy", "🎿 Dzieci i Szkoła", "Checklista pakowania na ferie zimowe w górach – odzież termoaktywna, sprzęt i apteczka.", [
        ("🎿 Sprzęt na stok i Bezpieczeństwo", [
            "Kask narciarski / snowboardowy (obowiązkowy na stoku!)",
            "Gogle narciarskie dopasowane do kasku",
            "Narty + kijki + buty (lub karta wypożyczenia / gotówka na wypożyczalnię)",
            "Rękawice narciarskie wodoodporne (2 pary – jedna zawsze schnie!)",
            "Kominiarka termoaktywna pod kask (min. 2 sztuki)"
        ]),
        ("🧥 Odzież zimowa i Termoaktywna", [
            "Kurtka narciarska z membraną i pasem śnieżnym",
            "Spodnie narciarskie (najlepiej dwie pary lub jedne + spodnie softshell)",
            "Bielizna termoaktywna – góra i dół (min. 3 komplety)",
            "Skarpety narciarskie wysokie (3–4 pary)",
            "Ciepły polar lub bluza techniczna (druga warstwa)",
            "Czapka zimowa i komin/szalik na spacery poza stokiem",
            "Ubrania po ośrodku: dresy, T-shirty, bielizna codzienna, kapcie"
        ]),
        ("🥾 Obuwie i Higiena Zimowa", [
            "Śniegowce lub wysokie, nieprzemakalne buty zimowe",
            "Klapki pod prysznic i na basen + strój kąpielowy (jeśli w planie są termy)",
            "Tłusty krem zimowy do twarzy (bez wody w składzie!) z filtrem UV",
            "Pomadka ochronna do ust na mróz",
            "Ręczniki, kosmetyczka, suszarka podróżna",
            "Mały termos na ciepłą herbatę do plecaka"
        ])
    ]),
    ("wycieczka-szkolna", "Co zabrać na wycieczkę szkolną (1-dniową i 3-dniową)", "🚌 Dzieci i Szkoła", "Szybka lista dla ucznia i rodzica na wycieczkę klasową lub zieloną szkołę.", [
        ("🎒 Wycieczka 1-dniowa (Do małego plecaka)", [
            "Ważna legitymacja szkolna",
            "Woda niegazowana (min. 1–1.5L, bez słodkich napojów gazowanych)",
            "Kanapki w sztywnym pudełku śniadaniowym (lunchbox)",
            "Przekąski, które się nie roztopią (jabłko, precelki, baton zbożowy – bez czekolady!)",
            "Kurtka przeciwdeszczowa lub peleryna",
            "Czapka z daszkiem i chusteczki higieniczne",
            "Leki na chorobę lokomocyjną (na drogę powrotną!) + mały woreczek foliowy",
            "Drobne kieszonkowe + naładowany telefon"
        ]),
        ("🧳 Dodatki na wycieczkę 2–3 dniową (Z noclegiem)", [
            "Bielizna, skarpetki i koszulki na każdy dzień + 1 komplet zapasowy",
            "Ciepła bluza i wygodne długie spodnie",
            "Piżama, klapki pod prysznic i ręcznik",
            "Szczoteczka do zębów, pasta i mały żel pod prysznic",
            "Ładowarka do telefonu / powerbank",
            "Worek na brudne rzeczy"
        ])
    ]),
    ("biwak-pod-namiotem", "Co zabrać na biwak pod namiot i kemping – Kompletna lista", "🏕️ Turystyka i Wyjazdy", "Praktyczny niezbędnik biwakowy: spanie, kuchnia polowa, oświetlenie i apteczka.", [
        ("⛺ Nocleg i Obozowisko", [
            "Namiot + komplet śledzi/szpilek, stelaż i odciągi",
            "Śpiwór dopasowany do temperatury nocnej",
            "Mata samopompująca, dmuchana lub karimata izolacyjna",
            "Poduszka turystyczna (lub poszewka na polar)",
            "Plandeka (tarp) lub folia ochronna pod podłogę namiotu"
        ]),
        ("🍳 Kuchnia biwakowa i Prowiant", [
            "Kuchenka turystyczna (palnik) + pełny kartusz z gazem",
            "Zapalniczka piezoelektryczna, zapałki sztormowe lub krzesiwo",
            "Menażka / lekki garnek z pokrywką + kubek stalowy/tytanowy",
            "Niezbędnik sztućcowy (spork) i ostry nóż obozowy / scyzoryk",
            "Zapas wody pitnej (min. 3L na osobę) lub filtr do wody",
            "Kawa, herbata, liofilizaty, owsianka, konserwy / batony energetyczne",
            "Gąbeczka, kropla biodegradowalnego płynu do naczyń i mocne worki na śmieci"
        ]),
        ("🔦 Oświetlenie, Narzędzia i Higiena", [
            "Latarka czołowa (czołówka) + zapasowe baterie lub kabel ładowania",
            "Powerbank o dużej pojemności (10 000 – 20 000 mAh)",
            "Taśma naprawcza (duct tape), kilka trytytek i linka paracord (5–10m)",
            "Repelent na komary i kleszcze + kleszczołapki",
            "Apteczka osobista + papier toaletowy w strunowym worku wodoodpornym",
            "Ręcznik szybkoschnący z mikrofibry"
        ])
    ]),
    ("bagaz-podreczny-samolot", "Bagaż podręczny do samolotu i na City Break (3–5 dni)", "✈️ Turystyka i Wyjazdy", "Lista rzeczy do plecaka kabinowego (40x30x20 / 55x40x20) zgodna z limitami linii lotniczych.", [
        ("🛂 Dokumenty i Kontrola Bezpieczeństwa", [
            "Dowód osobisty (UE/Schengen) lub ważny Paszport",
            "Karta pokładowa w aplikacji linii lotniczej (oraz pobrana offline w PDF)",
            "Karta EKUZ + polisa ubezpieczenia turystycznego",
            "Karta płatnicza wielowalutowa + drobna gotówka w lokalnej walucie",
            "Torebka strunowa 1L z płynami w pojemnikach max. 100 ml każdy!"
        ]),
        ("📱 Elektronika (Wyłącznie w bagażu podręcznym!)", [
            "Powerbank (do 100 Wh / ok. 27 000 mAh – zakaz wkładania do rejestrowanego!)",
            "Szybka ładowarka sieciowa (najlepiej wieloportowa) + kable USB",
            "Słuchawki dokanałowe + pobrane mapy offline i bilety",
            "Pusta butelka na wodę (do napełnienia po przejściu kontroli bezpieczeństwa)"
        ]),
        ("👕 Odzież kapsułowa (Na 3–4 dni)", [
            "Najcięższe buty, spodnie i bluza/kurtka założone NA SIEBIE do samolotu",
            "Bielizna i skarpetki na każdy dzień (zrolowane w organizerze)",
            "3–4 koszulki bazowe (T-shirt / merino)",
            "Lekka kurtka przeciwdeszczowa zwijana w kieszonkę",
            "Okulary przeciwsłoneczne"
        ]),
        ("🧴 Kosmetyczka Samolotowa (Bez problemu na bramkach)", [
            "Szczoteczka do zębów + mini-pasta (do 100 ml)",
            "Dezodorant w sztyfcie (stały – nie wlicza się do limitu płynów!)",
            "Szampon w kostce lub przelany do buteleczki podróżnej 50 ml",
            "Podstawowe leki (przeciwbólowe, plastry na otarcia od chodzenia)"
        ])
    ]),
    ("wyprawa-rowerowa-bikepacking", "Niezbędnik na wyprawę rowerową (Bikepacking / Sakwy)", "🚲 Rower i Hobby", "Lista sprzętu na wielodniowy wyjazd gravelowy lub szosowo-turystyczny.", [
        ("🔧 Narzędzia i Części Zapasowe w Trasie", [
            "2x dętka zapasowa (np. lekka TPU lub butylowa) + samoprzylepne łatki",
            "Zestaw naprawczy Tubeless (szydełko + sznurki/knoty butylowe) + 60 ml mleczka",
            "Multitool rowerowy ze skuwaczem do łańcucha + 2 spinki łańcucha (np. 10s/11s/12s)",
            "Pompka ręczna + łyżki do opon",
            "Zapasowy hak przerzutki dedykowany do Twojej ramy!",
            "1 para zapasowych klocków hamulcowych",
            "Wosk w płynie / oliwka do łańcucha + mała szmatka z mikrofibry",
            "Trytytki (opaski zaciskowe – różna długość) i kawałek taśmy izolacyjnej"
        ]),
        ("🚴 Odzież na Rower i Poza Rowerem", [
            "2 pary spodenek z wkładką (bibsy) + krem przeciw otarciom (chamois cream)",
            "2 koszulki rowerowe + potówka siatkowa (base layer)",
            "Kurtka przeciwdeszczowa / wiatrówka pakowana do kieszonki",
            "Rękawki i nogawki ocieplające (lub lekka bluza na poranki)",
            "Zestaw obozowy do spania i wyjścia do sklepu (lekki T-shirt, szorty, klapki/ultralight)",
            "Okulary fotochromatyczne + kask + rękawiczki"
        ]),
        ("⚡ Elektronika i Nawigacja", [
            "Komputer rowerowy GPS z wgranymi śladami GPX trasy",
            "Przednia lampka (z funkcją odciętej wiązki) + tylna lampka radar/ostrzegawcza",
            "Powerbank min. 10 000 mAh + krótkie kable USB-C do ładowania w torbie na ramie",
            "Szybka ładowarka sieciowa 2–3 portowa (żeby w noclegu naładować wszystko z 1 gniazdka)"
        ])
    ]),
    ("niezbednik-rowerowy-edc", "Niezbędnik rowerzysty na każdy wyjazd (Podsiodłówka EDC)", "🚲 Rower i Hobby", "Co wozić w torebce podsiodłowej lub kieszonce na co dzień (trasy 20–100 km).", [
        ("🛞 Naprawa Kapcia (Zestaw Minimum)", [
            "Dętka w odpowiednim rozmiarze (z właściwą długością wentyla Presta/Schrader)",
            "2 mocne łyżki do opon (np. kompozytowe)",
            "Mini-pompka przy ramie lub pompka na naboje CO2 + 2 naboje 16g/25g",
            "Szydełko i knoty do opon bezdętkowych (jeśli jeździsz na Tubeless)"
        ]),
        ("🔩 Awaria Mechaniczna i Bezpieczeństwo", [
            "Multitool z kluczami imbusowymi (2–8 mm), Torx T25 i skuwaczem",
            "Zapasowa spinka do łańcucha (odpowiednia do rzędowości napędu)",
            "2–3 opaski zaciskowe (trytytki) + banknot 50 zł (awaryjna gotówka i łatka na rozciętą oponę)",
            "Karta ICE / dowód i naładowana tylna lampka"
        ])
    ]),
    ("zestaw-startowy-druk-3d", "Niezbędnik do Druku 3D – Narzędzia i akcesoria obok drukarki", "🔧 Rower i Hobby", "Lista niezbędnych narzędzi do post-processingu, konserwacji i bezproblemowego drukowania.", [
        ("🧼 Utrzymanie stołu i Konserwacja", [
            "Alkohol izopropylowy (IPA 99%) w butelce z atomizerem + ściereczka bezpyłowa",
            "Płyn do mycia naczyń bez balsamów (do okresowego mycia płyt PEI w ciepłej wodzie)",
            "Klej w sztyfcie lub preparat adhezyjny (jako separator przy druku z PETG / TPU)",
            "Suszarka do filamentu + szczelne worki strunowe z pochłaniaczem wilgoci (Silica Gel)",
            "Zapasowe dysze (np. 0.4 mm ze stali hartowanej do filamentów CF/GF oraz 0.6 mm)"
        ]),
        ("🔪 Obróbka wydruków (Post-processing) i Pomiary", [
            "Gratownik (deburring tool) z wymiennymi ostrzami do szybkiego usuwania 'stopy słonia'",
            "Precyzyjne cążki boczne (flush cutters) do wycinania podpór",
            "Szczypce wydłużone (igłowe) do wyrywania supportów z głębokich otworów",
            "Suwmiarka elektroniczna (do projektowania własnych części w CAD)",
            "Lutownica z regulacją temperatury + zestaw mosiężnych insertów gwintowanych (M2.5, M3, M4, M5)",
            "Mały palnik gazowy lub opalarka (do szybkiego usuwania nitek / stringingu)"
        ])
    ]),
    ("domowy-warsztat-narzedzia", "Niezbędnik domowego majsterkowicza – Skrzynka narzędziowa", "🔧 Rower i Hobby", "Podstawowy zestaw narzędzi do mieszkania i domu, którym naprawisz 95% usterek.", [
        ("🪛 Narzędzia Ręczne (Podstawa)", [
            "Wkrętaki (śrubokręty): krzyżakowe PH1, PH2, PZ2 oraz płaskie + próbnik napięcia",
            "Komplet kluczy imbusowych (1.5–10 mm) z kulką oraz kluczy Torx (T10–T40)",
            "Zestaw kluczy płasko-oczkowych (8, 10, 13, 17, 19 mm) + klucz nastawny ('francuz')",
            "Kombinerki uniwersalne, obcinaczki boczne oraz szczypce nastawne do rur (Knipex Cobra / żabka)",
            "Młotek ślusarski (300–500g) + gumowy pobijak",
            "Nóż z łamanym ostrzem 18 mm + zapasowe ostrza"
        ]),
        ("⚡ Elektronarzędzia i Pomiary", [
            "Wkrętarka akumulatorowa (12V lub 18V) z udarem lub młotowiertarka SDS+ (do wielkiej płyty/żelbetu)",
            "Zestaw wierteł do metalu (HSS), drewna i betonu (6, 8, 10 mm) + zestaw bitów udarowych",
            "Miarka zwijana (3m lub 5m) z blokadą",
            "Poziomica (40–60 cm) oraz kątownik stolarski",
            "Multimetr cyfrowy (do sprawdzania baterii, ciągłości przewodów i napięcia 230V)"
        ]),
        ("📦 Materiały Eksploatacyjne (Zawsze pod ręką)", [
            "Uniwersalne kołki rozporowe (np. Fischer DuoPower 6x30 i 8x40) z wkrętami",
            "Taśma izolacyjna, taśma malarska, taśma teflonowa (do gwintów hydraulicznych) i szara taśma zbrojona",
            "Klej cyjanoakrylowy (Super Glue), klej do drewna (Wikol) oraz preparat penetrujący (WD-40 / CX80)",
            "Zestaw opasek zaciskowych (trytytek) i podkładek filcowych pod meble"
        ])
    ]),
    ("torba-do-szpitala", "Co zabrać do szpitala (Planowy pobyt / Zabieg) – Lista rzeczy", "🏥 Dom i Bezpieczeństwo", "Praktyczna checklista rzeczy do szpitala na 2–5 dni – dokumenty, higiena i wygoda.", [
        ("📋 Dokumentacja Medyczna i Formalności", [
            "Dowód osobisty oraz skierowanie do szpitala (oryginał)",
            "Komplet dotychczasowych wyników badań, wypisów ze szpitala i płyt CD/pendrive z obrazowaniem (RTG, TK, MRI)",
            "Spisana na kartce lista wszystkich przyjmowanych na stałe leków wraz z dawkowaniem",
            "Leki przyjmowane na stałe w oryginalnych opakowaniach",
            "NIP pracodawcy (jeśli potrzebne będzie zwolnienie lekarskie L4)"
        ]),
        ("👕 Odzież i Obuwie na Oddział", [
            "Piżamy (min. 2–3 komplety – najlepiej z rozpinaną górą dla łatwego dostępu do badań/kroplówki)",
            "Cienki szlafrok lub rozpinana bluza dresowa",
            "Wygodne spodenki / spodnie dresowe do chodzenia po korytarzu",
            "Klapki pod prysznic (antypoślizgowe) oraz osobne kapcie/wsuwane buty do chodzenia po sali",
            "Bielizna osobista i skarpetki bezuciskowe (na każdy dzień + zapas)"
        ]),
        ("🧴 Higiena i Komfort (Praktyczne patenty)", [
            "Długi kabel do ładowarki (2–3 metry!) lub powerbank – gniazdka w salach są często daleko od łóżka",
            "Słuchawki do telefonu oraz zatyczki do uszu i opaska na oczy (do spania w sali wieloosobowej)",
            "Woda mineralna niegazowana w małych butelkach 0.5L z dzióbkiem (wygodne picie na leżąco)",
            "Własny kubek, sztućce (łyżka, widelec, bezpieczny nóż) i mała ściereczka/płyn do ich przemycia",
            "2 ręczniki (duży i mały), papier toaletowy, chusteczki nawilżane i żel antybakteryjny",
            "Szczoteczka, pasta do zębów, szary żel pod prysznic / hipoalergiczny"
        ])
    ]),
    ("kosmetyczka-apteczka-podrozna", "Niezbędnik kosmetyczki i apteczki wyjazdowej (Urlop / Góry)", "🏥 Dom i Bezpieczeństwo", "Uniwersalna lista kosmetyków i leków na wyjazd wakacyjny, dzięki której niczego nie zapomnisz.", [
        ("🩹 Apteczka Wyjazdowa (Pierwsza Pomoc i Leki)", [
            "Leki przeciwbólowe i przeciwgorączkowe (paracetamol / ibuprofen)",
            "Leki na dolegliwości żołądkowe (elektrolity w saszetkach, probiotyk, węgiel/diosmektyt, krople żołądkowe)",
            "Środek do odkażania ran w małym atomizerze (np. z oktenidyną)",
            "Zestaw plastrów z opatrunkiem + plastry hydrokoloidowe na pęcherze i obtarcia pięt",
            "Bandaż elastyczny, jałowe gaziki i mała pęseta / kleszczołapki",
            "Tabletki na ból gardła i krople do nosa oraz leki przeciwhistaminowe (na alergię / ukąszenia)"
        ]),
        ("🧴 Kosmetyczka Podróżna", [
            "Szczoteczka do zębów w osłonce, pasta i nić dentystyczna",
            "Żel pod prysznic i szampon (przelane do mniejszych pojemników podróżnych)",
            "Antyperspirant / dezodorant",
            "Krem z filtrem UV do twarzy i ciała + balsam po opalaniu (np. z pantenolem)",
            "Maszynka do golenia, obcinaczki do paznokci / pilniczek",
            "Soczewki kontaktowe + płyn do soczewek + okulary korekcyjne (jeśli używasz)"
        ])
    ]),
    ("niezbednik-awaryjny-brak-pradu", "Niezbędnik awaryjny na brak prądu (Blackout / Dom 72h)", "🏥 Dom i Bezpieczeństwo", "Checklista domowego zabezpieczenia na wypadek kilkudniowej awarii zasilania, ogrzewania lub sieci.", [
        ("🔦 Oświetlenie, Energia i Komunikacja", [
            "Latarki czołowe dla domowników + lampka kempingowa stojąca (bezpieczniejsza niż świece!)",
            "Zapas baterii alkalicznych (AA, AAA) oraz naładowane powerbanki",
            "Radio zasilane na baterie lub z dynamem na korbkę (do odbioru komunikatów lokalnych przy braku internetu)",
            "Gotówka w niskich nominałach (10, 20, 50 zł – w czasie blackoutu bankomaty i terminale w sklepach nie działają!)"
        ]),
        ("💧 Woda, Żywność i Ciepło (Na 3 doby)", [
            "Zapas wody pitnej w zgrzewkach (min. 3 litry na osobę na dobę) + woda techniczna",
            "Kuchenka turystyczna na kartusze gazowe + zapas 2–3 kartuszy (do zagotowania wody w bloku z płytą indukcyjną)",
            "Żywność o długim terminie niewymagająca lodówki (konserwy, suchary, orzechy, masło orzechowe, dania gotowe, kawa)",
            "Ciepłe koce, śpiwory i odzież termiczna (w razie wyłączenia pomp obiegowych CO)",
            "Czujnik tlenku węgla (czadu) na baterie – jeśli dogrzewasz dom kominkiem lub używasz gazu"
        ]),
        ("📄 Dokumenty i Apteczka", [
            "Zapas leków przyjmowanych na stałe na minimum 14 dni",
            "Teczka z oryginałami ważnych dokumentów (akty, polisy, paszporty, pendrive z kopią zdjęć/danych)",
            "Naładowana gaśnica domowa i apteczka pierwszej pomocy"
        ])
    ]),
    ("dom-przed-wyjazdem-na-urlop", "Zabezpieczenie mieszkania przed wyjazdem na urlop – Checklista", "🏠 Dom i Bezpieczeństwo", "Szybka lista kontrolna przed zamknięciem drzwi na wakacje lub dłuższy weekend.", [
        ("🚰 Woda, Gaz i Elektryka", [
            "Zakręcony główny zawór wody (oraz zawór dopływu do pralki i zmywarki)",
            "Wyłączone z gniazdek urządzenia w trybie stand-by (TV, komputer, ładowarki, ekspres do kawy, router)",
            "Sprawdzona i domknięta lodówka oraz zamrażarka (opróżniona z produktów psujących się)",
            "Zakręcony zawór gazu (jeśli posiadasz kuchenkę gazową)"
        ]),
        ("🪟 Okna, Drzwi i Porządek", [
            "Dokładnie zamknięte wszystkie okna (również z pozycji mikrowentylacji!) i drzwi balkonowe",
            "Wyrzucone wszystkie śmieci (szczególnie bio oraz kosz w łazience) i opróżniona zmywarka",
            "Wylana woda z podstawki pod ociekaczem i ekspresu do kawy",
            "Podlane kwiaty i zasłonięte częściowo rolety (ochrona przed nagrzewaniem)",
            "Zabrane klucze zapasowe, dokumenty i wyłączony budzik stacjonarny!"
        ])
    ]),
    ("niezbednik-malarski-remontowy", "Niezbędnik do malowania pokoju i szybkiego remontu", "🎨 Rower i Hobby", "Lista narzędzi i materiałów, o których najczęściej zapomina się w markecie budowlanym przed malowaniem.", [
        ("🛡️ Zabezpieczenie i Przygotowanie Ścian", [
            "Folia malarska (najlepiej grubsza LDPE na podłogę i cienka na meble)",
            "Taśma malarska papierowa (żółta/niebieska UV – min. 2–3 rolki o szerokości 30–38 mm)",
            "Masa szpachlowa naprawcza (gotowa w tubce/wiaderku) + szpachelka nierdzewna do ubytków po kołkach",
            "Papier ścierny / gąbka ścierna (gradacja 120–180) do zeszlifowania szpachli",
            "Mydło malarskie z wodą + szeroki pędzel ławkowiec lub gąbka do odtłuszczenia ścian",
            "Grunt podkładowy dopasowany do chłonności podłoża"
        ]),
        ("🖌️ Narzędzia do Malowania", [
            "Duży wałek z mikrofibry (18–25 cm) do ścian + mały wałek (10 cm) do trudno dostępnych miejsc",
            "Kij teleskopowy do wałka (oszczędza kręgosłup i zapewnia równy docisk!)",
            "Kuweta malarska + wymienne plastikowe wkłady do kuwety (lub kratka ociekowa do wiadra)",
            "Pędzel skośny (odcięciowy) do kątów, narożników i okolic gniazdek",
            "Mieszadło do farby (na wkrętarkę lub ręczne) + otwieracz do puszek",
            "Wkrętak (śrubokręt) do zdjęcia ramek gniazdek i włączników przed malowaniem"
        ])
    ])
]

# Wspólny widget HTML+JS dla kalkulatora Farby i Zaprawy/Betonu
PAINT_AND_MORTAR_WIDGET = """
<div class="timer-box" style="text-align:left;" id="paintCalcBox">
    <h2 style="margin-top:0;">🎨 Kalkulator Farby (Ile litrów na pokój / ściany?)</h2>
    <p style="font-size:0.9rem;">Wpisz łączną powierzchnię do pomalowania, odejmij okna/drzwi i oblicz potrzebną ilość farby wraz z 10% zapasem.</p>
    <div class="form-row">
        <div>
            <label for="pArea">Powierzchnia ścian/sufitu (m²):</label>
            <input type="number" id="pArea" value="45" min="1" step="1" oninput="calcPaint()">
        </div>
        <div>
            <label for="pOpenings">Liczba drzwi i okien (odlicza ~1.8 m²/szt.):</label>
            <input type="number" id="pOpenings" value="3" min="0" step="1" oninput="calcPaint()">
        </div>
    </div>
    <div class="form-row">
        <div>
            <label for="pLayers">Liczba warstw malowania:</label>
            <input type="number" id="pLayers" value="2" min="1" max="5" step="1" oninput="calcPaint()">
        </div>
        <div>
            <label for="pYield">Wydajność farby z puszki (m²/L):</label>
            <input type="number" id="pYield" value="12" min="1" step="0.5" oninput="calcPaint()">
        </div>
    </div>
    <button onclick="calcPaint()">Oblicz ilość farby</button>
    <div class="param-box" style="margin-top:1rem;" aria-live="polite">
        <div class="param-item"><div class="label">Powierzchnia netto (1 warstwa)</div><div class="val" id="pNetVal">39.6 m²</div></div>
        <div class="param-item"><div class="label">Potrzebna farba (+10% zapasu)</div><div class="val" id="pLitresVal">7.3 L</div></div>
    </div>
</div>

<div class="timer-box" style="text-align:left;" id="mortarCalcBox">
    <h2 style="margin-top:0;">🧱 Kalkulator Zaprawy i Betonu (Przelicznik na wiadra 10L i worki)</h2>
    <p style="font-size:0.9rem;">Praktyczne proporcje budowlane przeliczone na zwykłe wiadra budowlane (10 litrów) i worki cementu (25 kg).</p>
    <div class="form-row">
        <div>
            <label for="mType">Wybierz rodzaj mieszanki:</label>
            <select id="mType" onchange="calcMortar()">
                <option value="concrete">Beton roboczy B15/B20 – pod słupki, posadzkę, podmurówkę (1 : 2 : 3)</option>
                <option value="masonry">Zaprawa murarska / tynkarska cementowo-wapienna (1 : 1 : 6)</option>
                <option value="cement">Zaprawa czysto cementowa – mocna, podkładowa, reperacje (1 : 3)</option>
            </select>
        </div>
        <div>
            <label for="mBatches">Mnożnik zarobów (1 zarób = na 1 worek cementu 25 kg / ~20L):</label>
            <input type="number" id="mBatches" value="1" min="0.5" max="50" step="0.5" oninput="calcMortar()">
        </div>
    </div>
    <div id="mortarResBox" class="info-box" style="border-color:var(--accent); margin-top:0.5rem;"></div>
</div>

<script>
function calcPaint() {
    const area = parseFloat(document.getElementById('pArea').value) || 0;
    const openings = parseFloat(document.getElementById('pOpenings').value) || 0;
    const layers = parseFloat(document.getElementById('pLayers').value) || 1;
    const yieldL = parseFloat(document.getElementById('pYield').value) || 12;

    const netArea = Math.max(1, area - (openings * 1.8));
    const rawLitres = (netArea * layers) / yieldL;
    const totalWithMargin = rawLitres * 1.10;

    document.getElementById('pNetVal').textContent = netArea.toFixed(1) + " m²";
    document.getElementById('pLitresVal').textContent = totalWithMargin.toFixed(1) + " L";
}

function calcMortar() {
    const type = document.getElementById('mType').value;
    const b = parseFloat(document.getElementById('mBatches').value) || 1;
    const box = document.getElementById('mortarResBox');
    const isEn = (typeof currentLang !== 'undefined' && currentLang === 'en');

    if (type === 'concrete') {
        const cemBags = (1 * b).toFixed(1).replace('.0', '');
        const cemBuckets = (2 * b).toFixed(1).replace('.0', '');
        const sandBuckets = (4 * b).toFixed(1).replace('.0', '');
        const gravelBuckets = (6 * b).toFixed(1).replace('.0', '');
        const waterL = Math.round(11 * b);
        const yieldL = Math.round(80 * b);
        box.innerHTML = isEn
            ? `<h3>Proportion 1 : 2 : 3 (Output: ~${yieldL} L of wet concrete)</h3><ul><li><strong>Cement:</strong> ${cemBags} bag(s) 25 kg <em>(or ${cemBuckets} × 10L buckets)</em></li><li><strong>Sand (0–2 mm):</strong> ${sandBuckets} × 10L buckets</li><li><strong>Gravel / Aggregate (2–16 mm):</strong> ${gravelBuckets} × 10L buckets</li><li><strong>Water:</strong> approx. ${waterL} L (adjust for earth-moist consistency)</li></ul>`
            : `<h3>Proporcja objętościowa 1 : 2 : 3 (Uzyskasz ok. ${yieldL} litrów gotowego betonu)</h3><ul><li><strong>Cement:</strong> ${cemBags} worek 25 kg <em>(czyli ok. ${cemBuckets} wiadra 10L)</em></li><li><strong>Piasek płukany:</strong> ${sandBuckets} wiadra budowlane (po 10L)</li><li><strong>Żwir / Kruszywo (2–16 mm):</strong> ${gravelBuckets} wiader budowlanych (po 10L)</li><li><strong>Woda:</strong> ok. ${waterL} litrów (dolewaj stopniowo do konsystencji wilgotnej ziemi)</li></ul>`;
    } else if (type === 'masonry') {
        const cemBags = (1 * b).toFixed(1).replace('.0', '');
        const cemBuckets = (2 * b).toFixed(1).replace('.0', '');
        const limeBuckets = (2 * b).toFixed(1).replace('.0', '');
        const sandBuckets = (12 * b).toFixed(1).replace('.0', '');
        const waterL = Math.round(22 * b);
        box.innerHTML = isEn
            ? `<h3>Proportion 1 : 1 : 6 (Cement : Hydrated Lime : Sand)</h3><ul><li><strong>Cement:</strong> ${cemBags} bag(s) 25 kg <em>(${cemBuckets} × 10L buckets)</em></li><li><strong>Hydrated Lime:</strong> ${limeBuckets} × 10L buckets</li><li><strong>Sand:</strong> ${sandBuckets} × 10L buckets</li><li><strong>Water:</strong> approx. ${waterL} L</li></ul>`
            : `<h3>Proporcja objętościowa 1 : 1 : 6 (Cement : Wapno : Piasek)</h3><ul><li><strong>Cement:</strong> ${cemBags} worek 25 kg <em>(${cemBuckets} wiadra 10L)</em></li><li><strong>Wapno hydratyzowane:</strong> ${limeBuckets} wiadra budowlane (po 10L)</li><li><strong>Piasek:</strong> ${sandBuckets} wiader budowlanych (po 10L)</li><li><strong>Woda:</strong> ok. ${waterL} litrów</li></ul>`;
    } else {
        const cemBags = (1 * b).toFixed(1).replace('.0', '');
        const cemBuckets = (2 * b).toFixed(1).replace('.0', '');
        const sandBuckets = (6 * b).toFixed(1).replace('.0', '');
        const waterL = Math.round(10 * b);
        box.innerHTML = isEn
            ? `<h3>Proportion 1 : 3 (Pure Cement Mortar – High Strength)</h3><ul><li><strong>Cement:</strong> ${cemBags} bag(s) 25 kg <em>(${cemBuckets} × 10L buckets)</em></li><li><strong>Sand:</strong> ${sandBuckets} × 10L buckets</li><li><strong>Water:</strong> approx. ${waterL} L</li></ul>`
            : `<h3>Proporcja objętościowa 1 : 3 (Mocna zaprawa czysto cementowa)</h3><ul><li><strong>Cement:</strong> ${cemBags} worek 25 kg <em>(${cemBuckets} wiadra 10L)</em></li><li><strong>Piasek:</strong> ${sandBuckets} wiader budowlanych (po 10L)</li><li><strong>Woda:</strong> ok. ${waterL} litrów</li></ul>`;
    }
}
calcPaint();
calcMortar();
</script>
"""

# Liczniki liczone automatycznie z danych (nie wpisuj liczb ręcznie)
N_KUCH = len(KUCHNIA_ITEMS)
N_WARS = len(WARSZTAT_ITEMS) + 2          # + kalkulator farby i zaprawy
N_ROW = len(ROWER_ITEMS)
N_LIST = len(LISTY_ITEMS)
N_ALL = N_KUCH + N_WARS + N_ROW + N_LIST
SUBW = Counter(x[5] for x in WARSZTAT_ITEMS)
SUBR = Counter(x[5] for x in ROWER_ITEMS)
KUCH_POZ = f"{N_KUCH} {pl_plural(N_KUCH, 'pozycja', 'pozycje', 'pozycji')}"
WARS_POZ = f"{N_WARS} {pl_plural(N_WARS, 'pozycja', 'pozycje', 'pozycji')}"
ROW_POZ = f"{N_ROW} {pl_plural(N_ROW, 'pozycja', 'pozycje', 'pozycji')}"
LIST_BADGE = f"{N_LIST} {pl_plural(N_LIST, 'interaktywna lista', 'interaktywne listy', 'interaktywnych list')}"
ALL_POZ = f"{N_ALL} {pl_plural(N_ALL, 'pozycja', 'pozycje', 'pozycji')}"

# 4b. Wersja angielska (My Toolbelt): treści w content_en.py, powiązania adresów PL <-> EN
import sys
sys.path.insert(0, SCRIPT_DIR)
from content_en import WORKSHOP_EN, CYCLING_EN, CALC_EN, KITCHEN_EN, LISTS_EN

assert set(WORKSHOP_EN) <= {x[0] for x in WARSZTAT_ITEMS}, "content_en: nieznany slug warsztatu"
assert set(CYCLING_EN) <= {x[0] for x in ROWER_ITEMS}, "content_en: nieznany slug rowerowy"
N_WARS_EN = len(WORKSHOP_EN) + len(CALC_EN)
N_ROW_EN = len(CYCLING_EN)
assert set(KITCHEN_EN) <= {x[0] for x in KUCHNIA_ITEMS}, "content_en: nieznany slug kuchni"
assert set(LISTS_EN) <= {x[0] for x in LISTY_ITEMS}, "content_en: nieznany slug listy"
N_KUCH_EN = len(KITCHEN_EN)
N_LIST_EN = len(LISTS_EN)

def _pair(pl_rel, en_rel):
    ALT_PL2EN[pl_rel] = en_rel
    ALT_EN2PL[en_rel] = pl_rel

_pair("", "en/")
_pair("warsztat/", "en/workshop/")
_pair("rower/", "en/cycling/")
_pair("kuchnia/", "en/kitchen/")
_pair("listy/", "en/checklists/")
for _slug, _v in KITCHEN_EN.items():
    _pair(f"kuchnia/{_slug}.html", f"en/kitchen/{_v[0]}.html")
for _slug, _v in LISTS_EN.items():
    _pair(f"listy/{_slug}.html", f"en/checklists/{_v[0]}.html")
for _pl_rel, _v in CALC_EN.items():
    _pair(_pl_rel, _v[0])
for _slug, _v in WORKSHOP_EN.items():
    _pair(f"warsztat/{_slug}.html", f"en/workshop/{_v[0]}.html")
for _slug, _v in CYCLING_EN.items():
    _pair(f"rower/{_slug}.html", f"en/cycling/{_v[0]}.html")

all_urls = [
    f"{DOMAIN}/",
    f"{DOMAIN}/kuchnia/",
    f"{DOMAIN}/warsztat/",
    f"{DOMAIN}/rower/",
    f"{DOMAIN}/listy/"
]

# 6. Generowanie podstron Kuchnia
kuchnia_cards = []
for slug, title, temp, mins, tip in KUCHNIA_ITEMS:
    rel_url = f"kuchnia/{slug}.html"
    all_urls.append(f"{DOMAIN}/{rel_url}")
    kuchnia_cards.append(f'<a href="/{rel_url}" class="card" data-sub="airfryer"><span class="badge">🍳 Airfryer</span><h3>{title}</h3><p class="card-val">🌡️ {temp}°C  |  ⏱️ ~{mins} min</p></a>')
    
    is_meat = any(k in slug for k in ["kurczak", "udka", "skrzydelka", "nuggetsy", "karkowka", "schabowy", "mielone", "stek", "burger", "losos", "dorsz"])
    safety_banner = ""
    if is_meat:
        safety_banner = """<div class="alert-box alert-danger"><strong>🌡️ Bezpieczeństwo żywności:</strong> Podany czas ma charakter wyłącznie orientacyjny i zależy od grubości porcji oraz temperatury początkowej mięsa. Dla drobiu zawsze weryfikuj gotowość termometrem kuchennym w najgrubszym miejscu – bezpieczna temperatura wewnętrzna to <strong>minimum 74°C</strong>.</div>"""

    related_html = related_table(
        [(f"/kuchnia/{x[0]}.html", x[1], f"{x[2]}°C · ~{x[3]} min") for x in KUCHNIA_ITEMS if _is_meat(x[0]) == _is_meat(slug)],
        f"/{rel_url}", "Mięso i ryby w Airfryerze – zestawienie" if _is_meat(slug) else "Warzywa, przekąski i inne – zestawienie", "Produkt", "Temp. · czas")
    body = f"""
    <div class="breadcrumbs"><a href="/">Start</a> » <a href="/kuchnia/">Kuchnia</a> » {title}</div>
    <h1>{title} – Orientacyjny Czas i Temperatura</h1>
    <p>Punkt wyjścia dla frytkownic beztłuszczowych (Airfryer). Dostosuj czas do wielkości porcji i mocy swojego urządzenia.</p>
    {safety_banner}
    <div class="param-box">
        <div class="param-item"><div class="label">Temperatura startowa</div><div class="val">{temp}°C</div></div>
        <div class="param-item"><div class="label">Czas orientacyjny</div><div class="val">~{mins} min</div></div>
    </div>
    <div class="timer-box">
        <div class="wakelock-status" id="wlStatus">ℹ️ Status blokady wygaszania ekranu (Wake Lock): nieaktywna (włączy się po starcie)</div>
        <div class="timer-display" id="timer" aria-live="polite">{mins:02d}:00</div>
        <div>
            <button id="startBtn" onclick="toggleTimer({mins*60})">▶ Start</button>
            <button class="btn-secondary" onclick="resetTimer({mins*60})">↺ Reset</button>
        </div>
    </div>
    <h2>💡 Warunki przygotowania i wskazówki</h2>
    <div class="info-box"><p>{tip}</p></div>
    <h2>Kryteria sprawdzenia gotowości</h2>
    <div class="info-box">
        <ul>
            <li><strong>Ułożenie w koszu:</strong> Czas zakłada pieczenie w pojedynczej warstwie z zachowaniem przepływu gorącego powietrza. Przy pełnym koszu wydłuż czas o 20–30% i przemieszaj zawartość.</li>
            <li><strong>Stan początkowy:</strong> Produkty wyjęte bezpośrednio z głębokiego mrożenia lub bardzo grube kawałki wymagają dłuższego dopiekania w środku.</li>
            <li><strong>Kontrola przed końcem:</strong> Zajrzyj do szuflady na 2–3 minuty przed upływem czasu, a w przypadku mięsa i drobiu użyj termometru szpilkowego.</li>
        </ul>
    </div>
    {related_html}
    <p style="margin-top:1.5rem;"><a href="/kuchnia/" class="btn">← Wróć do pełnej tabeli Airfryer</a></p>
    <script>
    let interval = null, wakeLock = null, timeLeft = {mins*60}, isRunning = false;
    const wlEl = document.getElementById('wlStatus');
    const timerEl = document.getElementById('timer');
    const startBtn = document.getElementById('startBtn');

    async function requestWakeLock() {{
        if (!('wakeLock' in navigator)) {{
            wlEl.textContent = "⚠️ Twoja przeglądarka nie wspiera blokady ekranu (Wake Lock) – ekran może zgasnąć.";
            return;
        }}
        try {{
            wakeLock = await navigator.wakeLock.request('screen');
            wlEl.textContent = "🔒 Blokada wygaszania ekranu (Wake Lock): AKTYWNA";
            wlEl.style.color = "#10b981";
            wakeLock.addEventListener('release', () => {{
                if (isRunning) {{
                    wlEl.textContent = "⚠️ Blokada ekranu została zwolniona (np. przez przełączenie karty).";
                    wlEl.style.color = "#f59e0b";
                }}
            }});
        }} catch (err) {{
            wlEl.textContent = "⚠️ Nie udało się zablokować wygaszania ekranu (" + err.name + ").";
            wlEl.style.color = "#f59e0b";
        }}
    }}

    function releaseWakeLock() {{
        if (wakeLock !== null) {{
            wakeLock.release().catch(() => {{}});
            wakeLock = null;
        }}
        wlEl.textContent = "ℹ️ Blokada wygaszania ekranu: wyłączona";
        wlEl.style.color = "";
    }}

    document.addEventListener('visibilitychange', () => {{
        if (wakeLock !== null && document.visibilityState === 'visible' && isRunning) {{
            requestWakeLock();
        }}
    }});

    function playBeep() {{
        try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            [0, 0.3, 0.6].forEach(delay => {{
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, ctx.currentTime + delay);
                gain.gain.setValueAtTime(0.25, ctx.currentTime + delay);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(ctx.currentTime + delay);
                osc.stop(ctx.currentTime + delay + 0.2);
            }});
        }} catch(e) {{}}
    }}

    function updateDisplay() {{
        const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
        const s = String(timeLeft % 60).padStart(2, '0');
        timerEl.textContent = m + ":" + s;
    }}

    function toggleTimer(defaultSec) {{
        if (isRunning) {{
            clearInterval(interval);
            isRunning = false;
            startBtn.textContent = "▶ Wznów";
            releaseWakeLock();
            return;
        }}
        if (timeLeft <= 0) timeLeft = defaultSec;
        isRunning = true;
        startBtn.textContent = "⏸ Pauza";
        requestWakeLock();
        interval = setInterval(() => {{
            timeLeft--;
            if (timeLeft <= 0) {{
                clearInterval(interval);
                isRunning = false;
                timerEl.textContent = "KONIEC! 🔔";
                startBtn.textContent = "▶ Start";
                releaseWakeLock();
                playBeep();
                return;
            }}
            updateDisplay();
        }}, 1000);
    }}

    function resetTimer(defaultSec) {{
        clearInterval(interval);
        isRunning = false;
        timeLeft = defaultSec;
        updateDisplay();
        startBtn.textContent = "▶ Start";
        releaseWakeLock();
    }}
    </script>
    """
    save_file(rel_url, wrap_html(title, f"{title}: orientacyjna temperatura ({temp}°C), czas (~{mins} min), warunki bezpieczeństwa i minutnik online.", body, rel_url))

# 7. Generowanie podstron Warsztat + 2 nowe dedykowane podstrony kalkulatorów (Farba i Zaprawa/Beton)
warsztat_cards = []

paint_rel = "warsztat/kalkulator-farby.html"
all_urls.append(f"{DOMAIN}/{paint_rel}")
warsztat_cards.append(f'<a href="/{paint_rel}" class="card" data-sub="przeliczniki"><span class="badge">🎨 Remont i Budowa</span><h3>Kalkulator Farby na m² (Ile litrów na pokój / ściany?)</h3><p class="card-val">Odlicza okna/drzwi  |  +10% zapasu</p></a>')
paint_page_body = f"""
<div class="breadcrumbs"><a href="/">Start</a> » <a href="/warsztat/">Warsztat</a> » Kalkulator Farby</div>
<h1>Kalkulator Farby na m² – Ile litrów farby potrzebujesz na pokój?</h1>
{PAINT_AND_MORTAR_WIDGET}
<p style="margin-top:1.5rem;"><a href="/warsztat/" class="btn">← Wróć do wszystkich tabel warsztatowych</a></p>
"""
save_file(paint_rel, wrap_html("Kalkulator Farby na m² – Ile litrów na pokój i ściany?", "Szybki kalkulator zużycia farby na m² z odliczeniem drzwi i okien oraz 10% zapasem.", paint_page_body, paint_rel))

mortar_rel = "warsztat/proporcje-zaprawy-i-betonu.html"
all_urls.append(f"{DOMAIN}/{mortar_rel}")
warsztat_cards.append(f'<a href="/{mortar_rel}" class="card" data-sub="przeliczniki"><span class="badge">🧱 Remont i Budowa</span><h3>Proporcje Zaprawy i Betonu (Przelicznik na wiadra 10L i worki)</h3><p class="card-val">Beton 1:2:3  |  Zaprawa 1:1:6 i 1:3</p></a>')
mortar_page_body = f"""
<div class="breadcrumbs"><a href="/">Start</a> » <a href="/warsztat/">Warsztat</a> » Proporcje Zaprawy i Betonu</div>
<h1>Proporcje Zaprawy Murarskiej i Betonu – Przelicznik na wiadra 10L</h1>
{PAINT_AND_MORTAR_WIDGET}
<p style="margin-top:1.5rem;"><a href="/warsztat/" class="btn">← Wróć do wszystkich tabel warsztatowych</a></p>
"""
save_file(mortar_rel, wrap_html("Proporcje Zaprawy i Betonu na Wiadra 10L i Worki 25kg", "Praktyczny kalkulator i tabela proporcji betonu (1:2:3) oraz zaprawy murarskiej (1:1:6, 1:3) przeliczona na wiadra budowlane.", mortar_page_body, mortar_rel))

SUB_LABELS_W = {
    "gwinty": "🔩 Gwinty",
    "stal": "🔥 Obróbka cieplna",
    "druk3d": "🖨️ Druk 3D",
    "elektryka": "⚡ Elektryka (Informacyjnie)",
    "przeliczniki": "📐 Przeliczniki i Budowa"
}

for slug, title, val1, val2, tip, sub_cat in WARSZTAT_ITEMS:
    rel_url = f"warsztat/{slug}.html"
    all_urls.append(f"{DOMAIN}/{rel_url}")
    badge_txt = SUB_LABELS_W.get(sub_cat, "🔧 Warsztat")
    warsztat_cards.append(f'<a href="/{rel_url}" class="card" data-sub="{sub_cat}"><span class="badge">{badge_txt}</span><h3>{title}</h3><p class="card-val">{val1}  |  {val2}</p></a>')

    extra_alert = ""
    conditions_html = ""
    if sub_cat == "elektryka":
        extra_alert = """<div class="alert-box alert-danger"><strong>⚡ Ostrzeżenie: Dobór zależy od konkretnej instalacji!</strong> Podane na tej stronie przekroje i zabezpieczenia nie są gotową receptą montażową. Każdy obwód wymaga weryfikacji przez uprawnionego elektryka (obliczenie spadku napięcia, dobór do sposobu ułożenia przewodu, sprawdzenie impedancji pętli zwarcia oraz wytycznych producenta urządzenia).</div>"""
        conditions_html = """
        <h2>Wymagane warunki do sprawdzenia przed montażem</h2>
        <div class="info-box">
            <ul>
                <li><strong>Długość trasy i spadek napięcia:</strong> Przy długich odcinkach przekrój żyły trzeba zwiększyć, aby utrzymać dopuszczalny spadek napięcia.</li>
                <li><strong>Sposób ułożenia:</strong> Przewód ułożony w rurze osłonowej w ścianie ocieplonej wełną lub styropianem ma znacznie niższą obciążalność prądową niż przewód bezpośrednio w tynku.</li>
                <li><strong>Ochrona przeciwporażeniowa:</strong> Zastosowanie odpowiedniego wyłącznika różnicowoprądowego (np. dla ładowarek EV ochrona przed składową stałą > 6 mA DC) oraz pomiary końcowe instalacji.</li>
            </ul>
        </div>"""
    elif sub_cat == "gwinty":
        conditions_html = """
        <h2>Zakres zastosowania i normy warsztatowe</h2>
        <div class="info-box">
            <ul>
                <li><strong>Typ gwintu:</strong> Wartość główna dotyczy metrycznego gwintu zwykłego (ISO DIN 13-1) wykonywanego przez gwintowanie skrawające (nacinanie).</li>
                <li><strong>Gwintowniki wygniatające (bezwiórowe):</strong> Wymagają większej średnicy otworu wstępnego niż gwintowniki skrawające – sprawdź tabelę producenta narzędzia.</li>
                <li><strong>Gwinty drobnozwojne:</strong> Przed wierceniem zawsze zmierz skok gwintu śruby grzebieniem pomiarowym (szczególnie przy średnicach od M8 wzwyż w motoryzacji i częściach rowerowych).</li>
            </ul>
        </div>"""
    elif sub_cat == "stal":
        extra_alert = """<div class="alert-box"><strong>🔥 Uwaga technologiczna:</strong> Parametry obróbki cieplnej są orientacyjnymi zakresami katalogowymi. Przed hartowaniem zawsze zweryfikuj kartę materiałową (atest) od dostawcy danej partii stali.</div>"""
        conditions_html = """
        <h2>Warunki poprawnego procesu obróbki cieplnej</h2>
        <div class="info-box">
            <ul>
                <li><strong>Kontrola temperatury i czasu:</strong> Stale wysokostopowe (np. D2, 440C) wymagają stabilnego wygrzewania w piecu z regulatorem PID i zabezpieczenia przed odwęgleniem (folia hartownicza).</li>
                <li><strong>Medium chłodzące:</strong> Temperatura oleju hartowniczego (zwykle podgrzanego do 50–60°C) ma kluczowy wpływ na uniknięcie pęknięć hartowniczych.</li>
                <li><strong>Odpuszczanie:</strong> Wykonuj bezpośrednio po ostygnięciu detalu do ok. 50°C – pozostawienie zahartowanej stali bez odpuszczenia grozi jej samoistnym pęknięciem.</li>
            </ul>
        </div>"""
    elif sub_cat == "druk3d":
        conditions_html = """
        <h2>Warunki testowe i kalibracja</h2>
        <div class="info-box">
            <ul>
                <li><strong>Punkt startowy:</strong> Różni producenci filamentów oraz domieszki (Matte, Silk, CF, High-Speed) zmieniają temperaturę płynięcia nawet o 15–20°C.</li>
                <li><strong>Prędkość objętościowa (Volumetric Flow):</strong> Przy szybkim druku (np. >200 mm/s) konieczne jest podniesienie temperatury dyszy, aby rdzeń filamentu zdążył się stopić.</li>
            </ul>
        </div>"""
    else:
        conditions_html = """
        <h2>Dodatkowe informacje warsztatowe</h2>
        <div class="info-box">
            <p>Zawsze weryfikuj wymagania w instrukcji obsługi swojego urządzenia lub narzędzia przed zastosowaniem przeliczników w praktyce.</p>
        </div>"""

    related_html = related_table(
        [(f"/warsztat/{x[0]}.html", x[1], x[2]) for x in WARSZTAT_ITEMS if x[5] == sub_cat],
        f"/{rel_url}", f"Wszystkie pozycje: {SUB_LABELS_W.get(sub_cat, 'Warsztat')}", "Pozycja", "Wartość")
    body = f"""
    <div class="breadcrumbs"><a href="/">Start</a> » <a href="/warsztat/">Warsztat</a> » {title}</div>
    <h1>{title}</h1>
    <p>Szybka ściąga orientacyjna – zapoznaj się z warunkami zastosowania poniżej.</p>
    {extra_alert}
    <div class="param-box">
        <div class="param-item"><div class="label">Wartość orientacyjna</div><div class="val">{val1}</div></div>
        <div class="param-item"><div class="label">Szczegóły / Zakres</div><div class="val" style="font-size:1.35rem;">{val2}</div></div>
    </div>
    <h2>🛠️ Wskazówka praktyczna</h2>
    <div class="info-box"><p>{tip}</p></div>
    {conditions_html}
    {related_html}
    <p style="margin-top:1.5rem;"><a href="/warsztat/" class="btn">← Wróć do wszystkich tabel warsztatowych</a></p>
    """
    save_file(rel_url, wrap_html(title, f"{title} – orientacyjny parametr ({val1}) wraz z warunkami zastosowania.", body, rel_url))

# 8. Generowanie podstron Rower
rower_cards = []
SUB_LABELS_R = {
    "opony": "🛞 Opony i Ciśnienie",
    "serwis": "🔧 Montaż i Napęd",
    "dopasowanie": "📐 Dopasowanie i Trening"
}

for slug, title, val1, val2, tip, sub_cat in ROWER_ITEMS:
    rel_url = f"rower/{slug}.html"
    all_urls.append(f"{DOMAIN}/{rel_url}")
    badge_txt = SUB_LABELS_R.get(sub_cat, "🚲 Rower")
    rower_cards.append(f'<a href="/{rel_url}" class="card" data-sub="{sub_cat}"><span class="badge">{badge_txt}</span><h3>{title}</h3><p class="card-val">{val1}  |  {val2}</p></a>')

    extra_alert = ""
    if "cisnienie" in slug:
        extra_alert = """<div class="alert-box alert-danger"><strong>⚠️ Limity bezpieczeństwa (Obręcze Hookless i Opony):</strong> Podane wartości to <strong>ciśnienie startowe do dostrojenia</strong>, wyliczone dla <strong>masy całkowitej zestawu (kolarz + rower + ekwipunek)</strong>. Nigdy nie przekraczaj maksymalnego limitu wybitego na ściance bocznej opony ani limitu obręczy. Dla obręczy bezrantowych (<strong>Hookless</strong>) bezwzględny maksymalny limit wynosi zazwyczaj <strong>5.0 bar (72.5 PSI)</strong>!</div>"""
    elif "momenty" in slug:
        extra_alert = """<div class="alert-box"><strong>🔧 Ważne:</strong> Przykładowe wartości nie zastępują instrukcji konkretnego komponentu. Przed dokręceniem sprawdź oznaczenie momentu nadrukowane bezpośrednio na mostku, kierownicy lub sztycy.</div>"""

    related_html = related_table(
        [(f"/rower/{x[0]}.html", x[1], x[2]) for x in ROWER_ITEMS if x[5] == sub_cat],
        f"/{rel_url}", f"Wszystkie pozycje: {SUB_LABELS_R.get(sub_cat, 'Rower')}", "Pozycja", "Wartość")
    body = f"""
    <div class="breadcrumbs"><a href="/">Start</a> » <a href="/rower/">Rower</a> » {title}</div>
    <h1>{title}</h1>
    <p>Orientacyjne zestawienie parametrów dla rowerów gravelowych, MTB i szosowych – sprawdź zakres i warunki poniżej.</p>
    {extra_alert}
    <div class="param-box">
        <div class="param-item"><div class="label">Punkt startowy / Parametr</div><div class="val">{val1}</div></div>
        <div class="param-item"><div class="label">Wariant / Szczegóły</div><div class="val" style="font-size:1.35rem;">{val2}</div></div>
    </div>
    <h2>🚲 Wskazówka serwisowa i warunki</h2>
    <div class="info-box"><p>{tip}</p></div>
    {related_html}
    <p style="margin-top:1.5rem;"><a href="/rower/" class="btn">← Wróć do kalkulatora i tabel rowerowych</a></p>
    """
    save_file(rel_url, wrap_html(title, f"{title} – punkt startowy ({val1}), limity bezpieczeństwa i wskazówki serwisowe.", body, rel_url))

wosk_cross_card = '<a href="/warsztat/wosk-do-lancucha-proporcje-parafina-ptfe.html" class="card" data-sub="serwis"><span class="badge">🔧 Montaż i Napęd</span><h3>Domowy wosk do łańcucha rowerowego: Proporcje i temperatura</h3><p class="card-val">500 g parafiny + 5 g PTFE  |  Kąpiel: 75–85°C</p></a>'

# 9. Generowanie 12 interaktywnych podstron w dziale Listy i Niezbędniki (/listy/)
listy_cards = []
for slug, title, badge_cat, desc, groups in LISTY_ITEMS:
    rel_url = f"listy/{slug}.html"
    all_urls.append(f"{DOMAIN}/{rel_url}")
    total_items = sum(len(items) for _, items in groups)
    listy_cards.append(f'<a href="/{rel_url}" class="card" data-sub="checklista"><span class="badge">{badge_cat}</span><h3>{title}</h3><p class="card-val">☑️ {total_items} pozycji  |  🖨️ Druk A4 / PDF</p></a>')

    groups_html = ""
    item_idx = 0
    for g_title, g_items in groups:
        lis = ""
        for it in g_items:
            lis += f'<li class="item-row" data-idx="{item_idx}"><input type="checkbox"><span>{it}</span></li>\n'
            item_idx += 1
        groups_html += f"""
        <div class="checklist-group">
            <div class="group-title">{g_title}</div>
            <ul class="item-list">
                {lis}
            </ul>
        </div>"""

    related_html = related_table(
        [(f"/listy/{x[0]}.html", x[1], sum(len(i) for _, i in x[4])) for x in LISTY_ITEMS if _badge_group(x[2]) == _badge_group(badge_cat)],
        f"/{rel_url}", f"Podobne listy: {_badge_group(badge_cat)}", "Lista", "Pozycji")
    body = f"""
    <div class="breadcrumbs"><a href="/">Start</a> » <a href="/listy/">Listy i Niezbędniki</a> » {title}</div>
    <h1>{title}</h1>
    <p>{desc} Zaznaczaj spakowane rzeczy – lista zapisuje się automatycznie na Twoim urządzeniu. Możesz też dopisać własne pozycje, wydrukować czystą kartkę A4 lub przesłać aktualny stan linkiem do bliskich.</p>

    <div class="checklist-action-bar">
        <div style="flex: 1 1 200px;">
            <strong id="counter" style="color:var(--accent); font-size:1.05rem;">Gotowe: 0 / {total_items} (0%)</strong>
            <div class="progress-wrap"><div class="progress-bar" id="progBar"></div></div>
        </div>
        <div style="display:flex; gap:0.35rem; flex-wrap:wrap;">
            <button onclick="window.print()">🖨️ Drukuj / PDF</button>
            <button class="btn-secondary" onclick="shareUrl()" id="shareBtn">🔗 Udostępnij stan</button>
            <button class="btn-secondary" onclick="sendViaEmail()">✉️ Wyślij e-mail</button>
            <button class="btn-secondary" onclick="resetList()">↺ Wyczyść</button>
        </div>
    </div>

    {groups_html}

    <div class="checklist-group">
        <div class="group-title">➕ Twoje własne pozycje (Dopisane do listy)</div>
        <div class="add-custom-box">
            <input type="text" id="customInput" placeholder="Dopisz własną rzecz (np. ulubiona maskotka, ładowarka do zegarka)..." onkeydown="if(event.key==='Enter') addCustomItem()">
            <button onclick="addCustomItem()" style="white-space:nowrap;">+ Dodaj pozycję</button>
        </div>
        <ul class="item-list" id="customList"></ul>
    </div>

    {related_html}
    <p style="margin-top:2rem;"><a href="/listy/" class="btn">← Zobacz wszystkie Listy i Niezbędniki</a></p>

    <script>
    const STORAGE_KEY = "mn_list_{slug}_v1";

    function getStored() {{
        try {{
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {{ checked: [], custom: [], customChecked: [] }};
        }} catch(e) {{
            return {{ checked: [], custom: [], customChecked: [] }};
        }}
    }}

    function saveStored(data) {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }}

    function updateStats() {{
        const allRows = document.querySelectorAll('.item-row');
        const checkedRows = document.querySelectorAll('.item-row.checked');
        const total = allRows.length;
        const done = checkedRows.length;
        const pct = total > 0 ? Math.round((done / total) * 100) : 0;
        document.getElementById('counter').textContent = `Spakowano / Gotowe: ${{done}} / ${{total}} (${{pct}}%)`;
        document.getElementById('progBar').style.width = pct + "%";
    }}

    function syncToStorage() {{
        const data = getStored();
        const checkedIdx = [];
        document.querySelectorAll('.item-row[data-idx]').forEach(row => {{
            if (row.classList.contains('checked')) {{
                checkedIdx.push(parseInt(row.getAttribute('data-idx'), 10));
            }}
        }});
        const customChecked = [];
        document.querySelectorAll('#customList .item-row').forEach(row => {{
            if (row.classList.contains('checked')) {{
                customChecked.push(row.getAttribute('data-custom'));
            }}
        }});
        data.checked = checkedIdx;
        data.customChecked = customChecked;
        saveStored(data);
        updateStats();
    }}

    function bindRowEvents(row) {{
        const cb = row.querySelector('input[type="checkbox"]');
        row.addEventListener('click', (e) => {{
            if (e.target.tagName === 'SMALL') return;
            if (e.target !== cb) cb.checked = !cb.checked;
            if (cb.checked) row.classList.add('checked');
            else row.classList.remove('checked');
            syncToStorage();
        }});
    }}

    function renderCustomItem(text, isChecked) {{
        const ul = document.getElementById('customList');
        const li = document.createElement('li');
        li.className = 'item-row' + (isChecked ? ' checked' : '');
        li.setAttribute('data-custom', text);
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = isChecked;
        const span = document.createElement('span');
        span.textContent = text;
        const delBtn = document.createElement('small');
        delBtn.textContent = '✖ Usuń';
        delBtn.style.cssText = 'margin-left:auto; color:var(--danger); cursor:pointer; font-weight:700; padding:0.2rem 0.4rem;';
        delBtn.onclick = (e) => {{
            e.stopPropagation();
            const d = getStored();
            d.custom = (d.custom || []).filter(t => t !== text);
            d.customChecked = (d.customChecked || []).filter(t => t !== text);
            saveStored(d);
            li.remove();
            updateStats();
        }};
        li.appendChild(cb);
        li.appendChild(span);
        li.appendChild(delBtn);
        ul.appendChild(li);
        bindRowEvents(li);
    }}

    function addCustomItem() {{
        const inp = document.getElementById('customInput');
        const val = inp.value.trim();
        if (!val) return;
        const data = getStored();
        if (!data.custom) data.custom = [];
        if (!data.custom.includes(val)) {{
            data.custom.push(val);
            saveStored(data);
            renderCustomItem(val, false);
            inp.value = "";
            updateStats();
        }}
    }}

    function initChecklist() {{
        let data = getStored();
        const params = new URLSearchParams(window.location.search);
        if (params.has('c')) {{
            const fromUrl = params.get('c').split(',').map(x => parseInt(x, 10)).filter(x => !isNaN(x));
            data.checked = fromUrl;
            if (params.has('add')) {{
                const added = params.get('add').split('|').map(s => s.trim()).filter(Boolean);
                added.forEach(item => {{
                    if (!data.custom.includes(item)) data.custom.push(item);
                }});
            }}
            saveStored(data);
        }}

        document.querySelectorAll('.item-row[data-idx]').forEach(row => {{
            const idx = parseInt(row.getAttribute('data-idx'), 10);
            const cb = row.querySelector('input[type="checkbox"]');
            if ((data.checked || []).includes(idx)) {{
                cb.checked = true;
                row.classList.add('checked');
            }}
            bindRowEvents(row);
        }});

        (data.custom || []).forEach(txt => {{
            const isC = (data.customChecked || []).includes(txt);
            renderCustomItem(txt, isC);
        }});

        updateStats();
    }}

    function shareUrl() {{
        const data = getStored();
        const url = new URL(window.location.origin + window.location.pathname);
        if (data.checked && data.checked.length > 0) {{
            url.searchParams.set('c', data.checked.join(','));
        }}
        if (data.custom && data.custom.length > 0) {{
            url.searchParams.set('add', data.custom.join('|'));
        }}
        const shareLink = url.toString();
        if (navigator.clipboard) {{
            navigator.clipboard.writeText(shareLink).then(() => {{
                const btn = document.getElementById('shareBtn');
                btn.textContent = "✅ Skopiowano link!";
                setTimeout(() => {{ btn.textContent = "🔗 Udostępnij stan"; }}, 2500);
            }});
        }} else {{
            prompt("Skopiuj poniższy link ze stanem swojej listy:", shareLink);
        }}
    }}

    function sendViaEmail() {{
        let body = "{title} (MójNiezbędnik.pl):\\n\\n";
        document.querySelectorAll('.checklist-group').forEach(grp => {{
            const gTitle = grp.querySelector('.group-title').textContent.trim();
            const rows = grp.querySelectorAll('.item-row');
            if (rows.length > 0) {{
                body += "=== " + gTitle + " ===\\n";
                rows.forEach(r => {{
                    const mark = r.classList.contains('checked') ? "[X]" : "[ ]";
                    const txt = r.querySelector('span').textContent.trim();
                    body += `${{mark}} ${{txt}}\\n`;
                }});
                body += "\\n";
            }}
        }});
        body += "Link do interaktywnej listy: " + window.location.href;
        window.location.href = `mailto:?subject=${{encodeURIComponent("{title}")}}&body=${{encodeURIComponent(body)}}`;
    }}

    function resetList() {{
        if (confirm("Czy na pewno chcesz odznaczyć wszystkie pozycje na tej liście?")) {{
            const data = getStored();
            data.checked = [];
            data.customChecked = [];
            saveStored(data);
            document.querySelectorAll('.item-row').forEach(r => {{
                r.classList.remove('checked');
                r.querySelector('input[type="checkbox"]').checked = false;
            }});
            if (window.history.replaceState) {{
                window.history.replaceState(null, null, window.location.pathname);
            }}
            updateStats();
        }}
    }}

    initChecklist();
    </script>
    """
    save_file(rel_url, wrap_html(title, f"{title} – interaktywna lista kontrolna z zapisem stanu, drukowaniem A4/PDF i wysyłką na e-mail.", body, rel_url))

# 10. Strony zbiorcze kategorii
KUCHNIA_INDEX = f"""
<h1>🍳 Niezbędnik Kuchenny – Orientacyjne Czasy i Temperatury Airfryer</h1>
<p>Wpisz nazwę produktu poniżej, aby przefiltrować listę (obsługuje wyszukiwanie bez polskich znaków):</p>
<div class="alert-box"><strong>Wskazówka:</strong> Wszystkie czasy są orientacyjne dla pojedynczej warstwy w koszu. Przy pieczeniu drobiu zawsze sprawdzaj temperaturę wewnętrzną termometrem (min. 74°C).</div>
<label for="q">Wyszukaj produkt:</label>
<input type="text" id="q" placeholder="🔍 Szukaj np. frytki, piers, kurczak, losos, jajka..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(kuchnia_cards)}
</div>
<div id="noRes" class="no-results">Brak pasujących pozycji. Spróbuj wpisać inną frazę.</div>
<script>
function filterCards() {{
    const q = normStr(document.getElementById('q').value);
    let visible = 0;
    document.querySelectorAll('#cards .card').forEach(c => {{
        const match = normStr(c.textContent).includes(q);
        c.style.display = match ? 'flex' : 'none';
        if (match) visible++;
    }});
    document.getElementById('noRes').style.display = visible === 0 ? 'block' : 'none';
}}
</script>
"""
save_file("kuchnia/index.html", wrap_html("Tabela Czasów i Temperatur Airfryer", "Orientacyjna ściąga czasów i temperatur pieczenia w Airfryerze z wbudowanym minutnikiem i kryteriami gotowości.", KUCHNIA_INDEX, "kuchnia/"))

WARSZTAT_INDEX = f"""
<h1>🔧 Niezbędnik Warsztatowy i Remontowy – Gwinty, Stal, Druk 3D, Kalkulatory</h1>
{PAINT_AND_MORTAR_WIDGET}
<h2>Wszystkie tabele warsztatowe i budowlane</h2>
<p>Wybierz podkategorię poniżej lub wpisz szukany parametr (np. M8, farba, beton, 1.2842, PETG, 1:50):</p>
<div class="filter-bar" role="group" aria-label="Filtr podkategorii warsztatowych">
    <button class="filter-btn active" onclick="setSub('all', this)">Wszystkie ({N_WARS})</button>
    <button class="filter-btn" onclick="setSub('gwinty', this)">🔩 Gwinty ({SUBW['gwinty']})</button>
    <button class="filter-btn" onclick="setSub('stal', this)">🔥 Stal i Hartowanie ({SUBW['stal']})</button>
    <button class="filter-btn" onclick="setSub('druk3d', this)">🖨️ Druk 3D ({SUBW['druk3d']})</button>
    <button class="filter-btn" onclick="setSub('elektryka', this)">⚡ Elektryka ({SUBW['elektryka']})</button>
    <button class="filter-btn" onclick="setSub('przeliczniki', this)">📐 Budowa i Przeliczniki ({SUBW['przeliczniki'] + 2})</button>
</div>
<label for="q">Szukaj w warsztacie:</label>
<input type="text" id="q" placeholder="🔍 Wpisz np. farba, beton, m8, 440c, nmv, petg, wallbox..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(warsztat_cards)}
</div>
<div id="noRes" class="no-results">Brak pasujących pozycji dla wybranych kryteriów.</div>
<script>
let currentSub = 'all';
function setSub(sub, btn) {{
    currentSub = sub;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterCards();
}}
function filterCards() {{
    const q = normStr(document.getElementById('q').value);
    let visible = 0;
    document.querySelectorAll('#cards .card').forEach(c => {{
        const matchSub = (currentSub === 'all' || c.getAttribute('data-sub') === currentSub);
        const matchText = normStr(c.textContent).includes(q);
        const show = matchSub && matchText;
        c.style.display = show ? 'flex' : 'none';
        if (show) visible++;
    }});
    document.getElementById('noRes').style.display = visible === 0 ? 'block' : 'none';
}}
</script>
"""
save_file("warsztat/index.html", wrap_html("Tabele Warsztatowe: Kalkulator Farby, Betonu, Wiertła pod gwinty, Hartowanie", "Szybkie kalkulatory i tabele warsztatowe: kalkulator farby i betonu, średnice wierteł pod gwinty M2-M20, hartowanie stali, druk 3D.", WARSZTAT_INDEX, "warsztat/"))

ROWER_INDEX = f"""
<h1>🚲 Niezbędnik Rowerowy – Kalkulator Ciśnienia Startowego i Tabele</h1>
<div class="timer-box" style="text-align:left;">
    <h2 style="margin-top:0;">Kalkulator ciśnienia startowego w oponach (Gravel / MTB / Szosa)</h2>
    <p style="font-size:0.9rem;">Oblicza orientacyjny punkt wyjścia na podstawie <strong>masy całkowitej zestawu</strong> oraz szerokości opony.</p>
    <label for="weight">Masa całkowita zestawu: kolarz + rower + ekwipunek (40 – 170 kg):</label>
    <input type="text" inputmode="decimal" id="weight" value="105">
    <label for="width">Rzeczywista szerokość opony (mm):</label>
    <select id="width">
        <option value="25">25 mm (Szosa 700×25c / 25-622)</option>
        <option value="28">28 mm (Szosa 700×28c / 28-622)</option>
        <option value="32">32 mm (Road Plus 700×32c / 32-622)</option>
        <option value="35">35 mm (Gravel 700×35c / 35-622)</option>
        <option value="40" selected>40 mm (Gravel 700×40c / 40-622)</option>
        <option value="45">45 mm (Gravel 700×45c / 45-622)</option>
        <option value="50">50 mm (Monstercross / MTB 29×2.0 / 50-622)</option>
        <option value="57">57 mm (MTB 29×2.25 / 57-622)</option>
    </select>
    <label for="setup">System montażu i typ obręczy:</label>
    <select id="setup">
        <option value="tube">Z dętką (obręcz standardowa Hooked)</option>
        <option value="tubeless_hooked">Tubeless z mleczkiem (obręcz z haczykiem Hooked)</option>
        <option value="tubeless_hookless">Tubeless na obręczy bezrantowej (HOOKLESS – limit 5.0 bar!)</option>
    </select>
    <button onclick="calcPressure()">Oblicz ciśnienie startowe</button>
    <div id="calcWarn" class="alert-box alert-danger" style="display:none; margin-top:1rem;"></div>
    <div id="res" class="param-box" style="margin-top:1rem;" aria-live="polite">
        <div class="param-item"><div class="label">Przód (Startowe)</div><div class="val" id="pFront">2.5 bar</div></div>
        <div class="param-item"><div class="label">Tył (Startowe)</div><div class="val" id="pRear">2.7 bar</div></div>
    </div>
    <p style="font-size:0.82rem; margin-top:0.5rem; margin-bottom:0;"><strong>Metoda i limity:</strong> Kalkulator przyjmuje rozkład masy ok. 46% przód / 54% tył oraz współczynnik objętości opony. Dla systemu Hookless automatycznie wymusza górny limit bezpieczeństwa <strong>5.0 bar (72.5 PSI)</strong>. Zawsze sprawdź dopuszczalne ciśnienie na ściance opony i obręczy.</p>
</div>

<h2>Wszystkie ściągi i tabele rowerowe</h2>
<div class="filter-bar" role="group" aria-label="Filtr podkategorii rowerowych">
    <button class="filter-btn active" onclick="setSub('all', this)">Wszystkie ({N_ROW + 1})</button>
    <button class="filter-btn" onclick="setSub('opony', this)">🛞 Opony i Mleczko ({SUBR['opony']})</button>
    <button class="filter-btn" onclick="setSub('serwis', this)">🔧 Montaż i Napęd ({SUBR['serwis'] + 1})</button>
    <button class="filter-btn" onclick="setSub('dopasowanie', this)">📐 Dopasowanie i Trening ({SUBR['dopasowanie']})</button>
</div>
<label for="q">Szukaj w dziale rowerowym:</label>
<input type="text" id="q" placeholder="🔍 Szukaj np. 40c, 40-622, mleczko, wosk, momenty Nm..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(rower_cards) + wosk_cross_card}
</div>
<div id="noRes" class="no-results">Brak pasujących pozycji rowerowych.</div>
<script>
function calcPressure() {{
    const rawW = document.getElementById('weight').value.replace(',', '.');
    let w = parseFloat(rawW);
    const warnEl = document.getElementById('calcWarn');
    warnEl.style.display = 'none';

    if (isNaN(w) || w < 40 || w > 170) {{
        warnEl.textContent = "⚠️ Podaj prawidłową masę całkowitą zestawu (kolarz + rower + ekwipunek) w zakresie od 40 do 170 kg.";
        warnEl.style.display = 'block';
        w = Math.min(170, Math.max(40, isNaN(w) ? 95 : w));
        document.getElementById('weight').value = w;
    }}

    const width = parseFloat(document.getElementById('width').value) || 40;
    const setup = document.getElementById('setup').value;
    const isTl = setup.startsWith('tubeless');
    const isHookless = (setup === 'tubeless_hookless');

    let base = (w / (width * 1.48));
    if (width <= 32) base *= 1.95;
    if (isTl) base *= 0.88;

    let front = Math.max(1.1, (base * 0.94));
    let rear = Math.max(1.2, (base * 1.03));

    if (isHookless) {{
        if (width < 28) {{
            warnEl.innerHTML = "🚨 <strong>UWAGA (Hookless):</strong> Większość producentów obręczy bezrantowych (Hookless) zabrania montażu opon węższych niż 28 mm (700×28c)! Sprawdź tabelę kompatybilności producenta kół. Maksymalne ciśnienie ograniczono do 5.0 bar.";
            warnEl.style.display = 'block';
        }} else if (front > 5.0 || rear > 5.0) {{
            warnEl.innerHTML = "⚠️ <strong>Limit Hookless (5.0 bar):</strong> Wyliczone ciśnienie przekroczyło dopuszczalny limit dla obręczy bezrantowych. Wartość została ograniczona do maksymalnych 5.0 bar (72.5 PSI)!";
            warnEl.style.display = 'block';
        }}
        front = Math.min(5.0, front);
        rear = Math.min(5.0, rear);
    }}

    document.getElementById('pFront').textContent = front.toFixed(1) + " bar";
    document.getElementById('pRear').textContent = rear.toFixed(1) + " bar";
}}

let currentSub = 'all';
function setSub(sub, btn) {{
    currentSub = sub;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterCards();
}}
function filterCards() {{
    const q = normStr(document.getElementById('q').value);
    let visible = 0;
    document.querySelectorAll('#cards .card').forEach(c => {{
        const matchSub = (currentSub === 'all' || c.getAttribute('data-sub') === currentSub);
        const matchText = normStr(c.textContent).includes(q);
        const show = matchSub && matchText;
        c.style.display = show ? 'flex' : 'none';
        if (show) visible++;
    }});
    document.getElementById('noRes').style.display = visible === 0 ? 'block' : 'none';
}}
calcPressure();
</script>
"""
save_file("rower/index.html", wrap_html("Kalkulator Ciśnienia w Oponach i Tabele Rowerowe", "Oblicz ciśnienie startowe w oponach gravelowych, MTB i szosowych z uwzględnieniem limitów Hookless i masy zestawu.", ROWER_INDEX, "rower/"))

LISTY_INDEX = f"""
<h1>🎒 Interaktywne Listy Pakowania i Niezbędniki (Do druku A4 / PDF)</h1>
<p>Wybierz sytuację poniżej, odhaczaj spakowane przedmioty bezpośrednio na telefonie, dopisuj własne rzeczy, drukuj czystą kartkę A4 lub prześlij odhaczoną listę linkiem do bliskich:</p>
<label for="q">Szukaj listy lub niezbędnika:</label>
<input type="text" id="q" placeholder="🔍 Szukaj np. obóz, kolonie, zimowisko, biwak, szpital, samolot, bikepacking, remont..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(listy_cards)}
</div>
<div id="noRes" class="no-results">Brak pasujących list pakowania.</div>
<script>
function filterCards() {{
    const q = normStr(document.getElementById('q').value);
    let visible = 0;
    document.querySelectorAll('#cards .card').forEach(c => {{
        const match = normStr(c.textContent).includes(q);
        c.style.display = match ? 'flex' : 'none';
        if (match) visible++;
    }});
    document.getElementById('noRes').style.display = visible === 0 ? 'block' : 'none';
}}
</script>
"""
save_file("listy/index.html", wrap_html("Listy Pakowania na Wyjazd, Obóz, Biwak i Niezbędniki Hobbystyczne", "Interaktywne checklisty do odhaczania na telefonie i druku A4/PDF: co zabrać na obóz, kolonie, zimowisko, biwak, do szpitala i na wyprawę rowerową.", LISTY_INDEX, "listy/"))

# 11. Strona główna mojniezbednik.pl (4 główne działy + wyszukiwarka wszystkich narzędzi)
all_cards = listy_cards + kuchnia_cards + warsztat_cards + rower_cards

HOME_BODY = f"""
<h1>⚡ MójNiezbędnik.pl – Praktyczne parametry, tabele i interaktywne listy</h1>
<p>Szybkie punkty wyjścia z podanymi warunkami oraz interaktywne checklisty do druku – bez zbędnych wstępów. Wybierz dział lub wyszukaj narzędzie poniżej:</p>
<div class="grid" style="margin-bottom:2rem;">
    <a href="/listy/" class="card cat-card" style="border-color:var(--accent);">
        <span class="badge">{LIST_BADGE}</span>
        <h3>{ICON['lists']}Listy i Niezbędniki</h3>
        <p class="card-val">Co zabrać na obóz, kolonie, zimowisko, biwak, bikepacking i do szpitala (Druk A4 / PDF)</p>
    </a>
    <a href="/kuchnia/" class="card cat-card" style="border-color:var(--accent);">
        <span class="badge">{KUCH_POZ}</span>
        <h3>{ICON['kitchen']}Kuchnia & Airfryer</h3>
        <p class="card-val">Orientacyjne czasy, kryteria temperatury (74°C dla drobiu) + minutnik z Wake Lock</p>
    </a>
    <a href="/warsztat/" class="card cat-card" style="border-color:var(--accent);">
        <span class="badge">{WARS_POZ} + Kalkulatory</span>
        <h3>{ICON['workshop']}Warsztat, Remont & DIY</h3>
        <p class="card-val">Kalkulator farby i betonu, wiertła pod gwinty M2–M20, obróbka cieplna stali, druk 3D</p>
    </a>
    <a href="/rower/" class="card cat-card" style="border-color:var(--accent);">
        <span class="badge">{ROW_POZ} + Kalkulator</span>
        <h3>{ICON['bike']}Rower & Serwis</h3>
        <p class="card-val">Kalkulator ciśnienia (Hooked / Hookless), dawki mleczka tubeless, momenty Nm</p>
    </a>
</div>

<h2>🔍 Wyszukiwarka wszystkich {N_ALL} narzędzi, kalkulatorów i list</h2>
<label for="q">Wpisz szukaną frazę (obsługuje zapytania bez polskich znaków i spacji, np. farba, beton, oboz, piers, m 8, 40-622):</label>
<input type="text" id="q" placeholder="Szukaj np. farba, beton, obóz, kurczak, M8, 1.2842, PETG, 40c..." oninput="filterHome()">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:0.5rem;">
    <span id="viewStatus" style="font-size:0.9rem; color:var(--muted);">Wyświetlono: 20 wybranych narzędzi i list</span>
    <button class="btn-secondary" id="toggleAllBtn" onclick="showAllTools()" style="padding:0.45rem 0.9rem; font-size:0.85rem;">Pokaż wszystkie {ALL_POZ}</button>
</div>
<div class="grid" id="homeCards">
{''.join(all_cards)}
</div>
<div id="noRes" class="no-results">Nie znaleziono pasującego narzędzia. Sprawdź pisownię lub przejdź bezpośrednio do wybranego działu powyżej.</div>
<script>
let showingAll = false;
const cards = Array.from(document.querySelectorAll('#homeCards .card'));
const featuredIndices = new Set([0,1,2,3,4, 12,13,14,15,16, 50,51,52,53,54, 88,89,90,91,92]);

function applyHomeView() {{
    const q = normStr(document.getElementById('q').value);
    const isEn = (typeof currentLang !== 'undefined' && currentLang === 'en');
    let visible = 0;
    cards.forEach((c, idx) => {{
        if (q.length > 0) {{
            const match = normStr(c.textContent).includes(q);
            c.style.display = match ? 'flex' : 'none';
            if (match) visible++;
        }} else {{
            const show = showingAll || featuredIndices.has(idx);
            c.style.display = show ? 'flex' : 'none';
            if (show) visible++;
        }}
    }});
    document.getElementById('noRes').style.display = visible === 0 ? 'block' : 'none';
    const statusEl = document.getElementById('viewStatus');
    const btnEl = document.getElementById('toggleAllBtn');
    if (q.length > 0) {{
        statusEl.textContent = isEn ? ("Search results: found " + visible + " items") : ("Wyniki wyszukiwania: znaleziono " + visible + " pozycji");
        btnEl.style.display = "none";
    }} else {{
        btnEl.style.display = "inline-block";
        if (showingAll) {{
            statusEl.textContent = isEn ? "Showing full catalog: all {N_ALL} tools & lists" : "Wyświetlono pełny katalog: wszystkie {N_ALL} narzędzi i list";
            btnEl.textContent = isEn ? "Collapse to 20 featured" : "Zwiń do 20 wybranych";
        }} else {{
            statusEl.textContent = isEn ? "Showing: 20 featured tools across 4 categories" : "Wyświetlono: 20 wybranych pozycji z 4 działów";
            btnEl.textContent = isEn ? "Show all {N_ALL} items" : "Pokaż wszystkie {ALL_POZ}";
        }}
    }}
}}

function filterHome() {{ applyHomeView(); }}
function showAllTools() {{
    showingAll = !showingAll;
    applyHomeView();
}}
applyHomeView();
</script>
"""
save_file("index.html", wrap_html("Szybkie Kalkulatory, Listy Pakowania, Czasy Airfryer i Tabele Warsztatowe", "Praktyczny niezbędnik online: kalkulator farby i betonu, listy rzeczy na obóz i biwak, czasy pieczenia w Airfryerze, tabele wierteł pod gwinty i kalkulator ciśnienia w oponach.", HOME_BODY, ""))

# 11b. Wersja angielska (My Toolbelt) – /en/
EN_WIDGET = """
<div class="timer-box" style="text-align:left;" id="paintCalcBox">
    <h2 style="margin-top:0;">🎨 Paint Calculator (how many litres for a room?)</h2>
    <p style="font-size:0.9rem;">Enter the total area to paint, deduct doors and windows, and get the amount of paint you need including a 10% margin.</p>
    <div class="form-row">
        <div>
            <label for="pArea">Wall / ceiling area (m²):</label>
            <input type="number" id="pArea" value="45" min="1" step="1" oninput="calcPaint()">
        </div>
        <div>
            <label for="pOpenings">Number of doors and windows (deducts ~1.8 m² each):</label>
            <input type="number" id="pOpenings" value="3" min="0" step="1" oninput="calcPaint()">
        </div>
    </div>
    <div class="form-row">
        <div>
            <label for="pLayers">Number of coats:</label>
            <input type="number" id="pLayers" value="2" min="1" max="5" step="1" oninput="calcPaint()">
        </div>
        <div>
            <label for="pYield">Paint coverage from the tin (m²/L):</label>
            <input type="number" id="pYield" value="12" min="1" step="0.5" oninput="calcPaint()">
        </div>
    </div>
    <button onclick="calcPaint()">Calculate paint</button>
    <div class="param-box" style="margin-top:1rem;" aria-live="polite">
        <div class="param-item"><div class="label">Net area (1 coat)</div><div class="val" id="pNetVal">39.6 m²</div></div>
        <div class="param-item"><div class="label">Paint needed (+10% margin)</div><div class="val" id="pLitresVal">7.3 L</div></div>
    </div>
    <p style="font-size:0.82rem; margin:0.5rem 0 0;">Tip: 1 m² ≈ 10.76 sq ft, 1 litre ≈ 0.26 US gallons.</p>
</div>

<div class="timer-box" style="text-align:left;" id="mortarCalcBox">
    <h2 style="margin-top:0;">🧱 Concrete &amp; Mortar Mix Calculator (10 L buckets and 25 kg bags)</h2>
    <p style="font-size:0.9rem;">Practical volume ratios converted to standard 10-litre buckets and 25 kg cement bags (metric, as sold in Europe).</p>
    <div class="form-row">
        <div>
            <label for="mType">Choose the mix:</label>
            <select id="mType" onchange="calcMortar()">
                <option value="concrete">General-purpose concrete (approx. C12/15–C16/20) – post footings, slabs, foundations (1 : 2 : 3)</option>
                <option value="masonry">Cement-lime masonry / render mortar (1 : 1 : 6)</option>
                <option value="cement">Pure cement mortar – strong, bedding, repairs (1 : 3)</option>
            </select>
        </div>
        <div>
            <label for="mBatches">Number of batches (1 batch = one 25 kg cement bag / ~20 L):</label>
            <input type="number" id="mBatches" value="1" min="0.5" max="50" step="0.5" oninput="calcMortar()">
        </div>
    </div>
    <div id="mortarResBox" class="info-box" style="border-color:var(--accent); margin-top:0.5rem;"></div>
</div>
""" + PAINT_AND_MORTAR_WIDGET[PAINT_AND_MORTAR_WIDGET.index("<script>"):]

workshop_cards_en = []
cycling_cards_en = []

# Kalkulatory
for _pl_rel, (en_rel, c_title, c_desc, c_h1, c_crumb) in CALC_EN.items():
    all_urls.append(f"{DOMAIN}/{en_rel}")
    if "paint" in en_rel:
        workshop_cards_en.append(f'<a href="/{en_rel}" class="card" data-sub="przeliczniki"><span class="badge">🎨 Renovation &amp; Building</span><h3>Paint Calculator per m² (how many litres for a room?)</h3><p class="card-val">Deducts doors/windows  |  +10% margin</p></a>')
    else:
        workshop_cards_en.append(f'<a href="/{en_rel}" class="card" data-sub="przeliczniki"><span class="badge">🧱 Renovation &amp; Building</span><h3>Concrete &amp; Mortar Mix Ratios (10 L buckets and bags)</h3><p class="card-val">Concrete 1:2:3  |  Mortar 1:1:6 and 1:3</p></a>')
    calc_body = f"""
<div class="breadcrumbs"><a href="/en/">Home</a> » <a href="/en/workshop/">Workshop</a> » {c_crumb}</div>
<h1>{c_h1}</h1>
{EN_WIDGET}
<p style="margin-top:1.5rem;"><a href="/en/workshop/" class="btn">← Back to all workshop tables</a></p>
"""
    save_file(en_rel, wrap_html(c_title, c_desc, calc_body, en_rel, lang="en"))

SUB_LABELS_W_EN = {
    "gwinty": "🔩 Threads",
    "stal": "🔥 Heat treatment",
    "druk3d": "🖨️ 3D printing",
    "przeliczniki": "📐 Conversions &amp; building",
}
COND_W_EN = {
    "gwinty": """
        <h2>Scope and workshop standards</h2>
        <div class="info-box">
            <ul>
                <li><strong>Thread type:</strong> the main value is for ISO metric coarse threads (ISO 261 / DIN 13-1) made with a cutting tap.</li>
                <li><strong>Forming (fluteless) taps:</strong> need a larger pilot hole than cutting taps – check the tool maker's chart.</li>
                <li><strong>Fine threads:</strong> always measure the bolt's pitch with a thread gauge before drilling (especially from M8 up, on cars and bicycle parts).</li>
            </ul>
        </div>""",
    "stal": """
        <h2>Conditions for a correct heat treatment</h2>
        <div class="info-box">
            <ul>
                <li><strong>Temperature and time control:</strong> high-alloy steels (e.g. D2, 440C) need a stable soak in a PID-controlled kiln and protection from decarburisation (heat-treat foil).</li>
                <li><strong>Quench medium:</strong> the temperature of the quench oil (usually warmed to 50–60°C) is key to avoiding quench cracks.</li>
                <li><strong>Tempering:</strong> temper right after the part cools to about 50°C – hardened steel left untempered can crack on its own.</li>
            </ul>
        </div>""",
    "druk3d": """
        <h2>Test conditions and calibration</h2>
        <div class="info-box">
            <ul>
                <li><strong>Starting point:</strong> different filament brands and blends (matte, silk, CF, high-speed) shift the melt temperature by as much as 15–20°C.</li>
                <li><strong>Volumetric flow:</strong> when printing fast (e.g. &gt;200 mm/s) raise the nozzle temperature so the core of the filament has time to melt.</li>
            </ul>
        </div>""",
}
COND_W_EN_DEFAULT = """
        <h2>Additional workshop notes</h2>
        <div class="info-box">
            <p>Always check the requirements in the manual for your device or tool before using conversion values in practice.</p>
        </div>"""

for slug, title_pl, val1_pl, val2_pl, tip_pl, sub_cat in WARSZTAT_ITEMS:
    if slug not in WORKSHOP_EN:
        continue
    en_slug, title, val1, val2, tip = WORKSHOP_EN[slug]
    rel_url = f"en/workshop/{en_slug}.html"
    all_urls.append(f"{DOMAIN}/{rel_url}")
    badge_txt = SUB_LABELS_W_EN.get(sub_cat, "🔧 Workshop")
    workshop_cards_en.append(f'<a href="/{rel_url}" class="card" data-sub="{sub_cat}"><span class="badge">{badge_txt}</span><h3>{title}</h3><p class="card-val">{val1}  |  {val2}</p></a>')
    extra_alert = ""
    if sub_cat == "stal":
        extra_alert = """<div class="alert-box"><strong>🔥 Technical note:</strong> heat-treatment parameters are typical catalogue ranges. Before hardening, always check the material data sheet (certificate) from the supplier of your batch of steel.</div>"""
    related_html = related_table(
        [(f"/en/workshop/{WORKSHOP_EN[x[0]][0]}.html", WORKSHOP_EN[x[0]][1], WORKSHOP_EN[x[0]][2]) for x in WARSZTAT_ITEMS if x[5] == sub_cat and x[0] in WORKSHOP_EN],
        f"/{rel_url}", f"All items: {SUB_LABELS_W_EN.get(sub_cat, 'Workshop')}", "Item", "Value")
    body = f"""
    <div class="breadcrumbs"><a href="/en/">Home</a> » <a href="/en/workshop/">Workshop</a> » {title}</div>
    <h1>{title}</h1>
    <p>Quick reference value – check the conditions of use below.</p>
    {extra_alert}
    <div class="param-box">
        <div class="param-item"><div class="label">Reference value</div><div class="val">{val1}</div></div>
        <div class="param-item"><div class="label">Details / range</div><div class="val" style="font-size:1.35rem;">{val2}</div></div>
    </div>
    <h2>🛠️ Practical tip</h2>
    <div class="info-box"><p>{tip}</p></div>
    {COND_W_EN.get(sub_cat, COND_W_EN_DEFAULT)}
    {related_html}
    <p style="margin-top:1.5rem;"><a href="/en/workshop/" class="btn">← Back to all workshop tables</a></p>
    """
    save_file(rel_url, wrap_html(title, f"{title} – reference value ({val1}) with conditions of use.", body, rel_url, lang="en"))

SUB_LABELS_R_EN = {
    "opony": "🛞 Tyres &amp; pressure",
    "serwis": "🔧 Assembly &amp; drivetrain",
    "dopasowanie": "📐 Bike fit &amp; training",
}
for slug, title_pl, val1_pl, val2_pl, tip_pl, sub_cat in ROWER_ITEMS:
    if slug not in CYCLING_EN:
        continue
    en_slug, title, val1, val2, tip = CYCLING_EN[slug]
    rel_url = f"en/cycling/{en_slug}.html"
    all_urls.append(f"{DOMAIN}/{rel_url}")
    badge_txt = SUB_LABELS_R_EN.get(sub_cat, "🚲 Cycling")
    cycling_cards_en.append(f'<a href="/{rel_url}" class="card" data-sub="{sub_cat}"><span class="badge">{badge_txt}</span><h3>{title}</h3><p class="card-val">{val1}  |  {val2}</p></a>')
    extra_alert = ""
    if "cisnienie" in slug:
        extra_alert = """<div class="alert-box alert-danger"><strong>⚠️ Safety limits (hookless rims and tyres):</strong> these are <strong>starting pressures to fine-tune</strong>, calculated for the <strong>total system weight (rider + bike + gear)</strong>. Never exceed the maximum printed on the tyre sidewall or the rim limit. For hookless rims the absolute maximum is usually <strong>5.0 bar (72.5 PSI)</strong>!</div>"""
    elif "momenty" in slug:
        extra_alert = """<div class="alert-box"><strong>🔧 Important:</strong> typical values do not replace the instructions for your specific component. Before tightening, check the torque marking printed on the stem, handlebar or seatpost.</div>"""
    related_html = related_table(
        [(f"/en/cycling/{CYCLING_EN[x[0]][0]}.html", CYCLING_EN[x[0]][1], CYCLING_EN[x[0]][2]) for x in ROWER_ITEMS if x[5] == sub_cat and x[0] in CYCLING_EN],
        f"/{rel_url}", f"All items: {SUB_LABELS_R_EN.get(sub_cat, 'Cycling')}", "Item", "Value")
    body = f"""
    <div class="breadcrumbs"><a href="/en/">Home</a> » <a href="/en/cycling/">Cycling</a> » {title}</div>
    <h1>{title}</h1>
    <p>Reference values for gravel, MTB and road bikes – check the range and conditions below.</p>
    {extra_alert}
    <div class="param-box">
        <div class="param-item"><div class="label">Starting point / value</div><div class="val">{val1}</div></div>
        <div class="param-item"><div class="label">Variant / details</div><div class="val" style="font-size:1.35rem;">{val2}</div></div>
    </div>
    <h2>🚲 Service tip and conditions</h2>
    <div class="info-box"><p>{tip}</p></div>
    {related_html}
    <p style="margin-top:1.5rem;"><a href="/en/cycling/" class="btn">← Back to the calculator and cycling tables</a></p>
    """
    save_file(rel_url, wrap_html(title, f"{title} – starting point ({val1}), safety limits and service tips.", body, rel_url, lang="en"))

wax_en = WORKSHOP_EN.get("wosk-do-lancucha-proporcje-parafina-ptfe")
wax_cross_card_en = ""
if wax_en:
    wax_cross_card_en = f'<a href="/en/workshop/{wax_en[0]}.html" class="card" data-sub="serwis"><span class="badge">🔧 Assembly &amp; drivetrain</span><h3>{wax_en[1]}</h3><p class="card-val">500 g paraffin + 5 g PTFE  |  Bath: 75–85°C</p></a>'

FILTER_JS_EN = """
<script>
let currentSub = 'all';
function setSub(sub, btn) {
    currentSub = sub;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterCards();
}
function filterCards() {
    const q = normStr(document.getElementById('q').value);
    let visible = 0;
    document.querySelectorAll('#cards .card').forEach(c => {
        const matchSub = (currentSub === 'all' || c.getAttribute('data-sub') === currentSub);
        const matchText = normStr(c.textContent).includes(q);
        const show = matchSub && matchText;
        c.style.display = show ? 'flex' : 'none';
        if (show) visible++;
    });
    document.getElementById('noRes').style.display = visible === 0 ? 'block' : 'none';
}
</script>
"""

SUBW_EN = Counter(x[5] for x in WARSZTAT_ITEMS if x[0] in WORKSHOP_EN)
SUBR_EN = Counter(x[5] for x in ROWER_ITEMS if x[0] in CYCLING_EN)

workshop_filters_en = [f"""<button class="filter-btn active" onclick="setSub('all', this)">All ({N_WARS_EN})</button>"""]
for _sub, _label in SUB_LABELS_W_EN.items():
    _n = SUBW_EN.get(_sub, 0) + (len(CALC_EN) if _sub == "przeliczniki" else 0)
    if _n:
        workshop_filters_en.append(f"""<button class="filter-btn" onclick="setSub('{_sub}', this)">{_label} ({_n})</button>""")

WORKSHOP_INDEX_EN = f"""
<h1>🔧 Workshop &amp; DIY Reference – Threads, Steel, 3D Printing, Calculators</h1>
{EN_WIDGET}
<h2>All workshop and building tables</h2>
<p>Pick a sub-category below or type what you're looking for (e.g. M8, paint, concrete, D2, PETG, 50:1):</p>
<div class="filter-bar" role="group" aria-label="Workshop sub-category filter">
    {chr(10).join(workshop_filters_en)}
</div>
<label for="q">Search the workshop:</label>
<input type="text" id="q" placeholder="🔍 e.g. paint, concrete, m8, 440c, o2, petg, 2-stroke..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(workshop_cards_en)}
</div>
<div id="noRes" class="no-results">No matching items for the selected criteria.</div>
<p style="font-size:0.85rem;">Electrical wiring tables are available only in the Polish version, because cable sizing rules differ between countries.</p>
{FILTER_JS_EN}
"""
save_file("en/workshop/index.html", wrap_html("Workshop Tables: Paint & Concrete Calculators, Tap Drill Sizes, Heat Treating", "Quick workshop calculators and tables: paint and concrete calculators, tap drill sizes M2–M20, steel heat treatment, 3D printing temperatures.", WORKSHOP_INDEX_EN, "en/workshop/", lang="en"))

cycling_filters_en = [f"""<button class="filter-btn active" onclick="setSub('all', this)">All ({N_ROW_EN + (1 if wax_cross_card_en else 0)})</button>"""]
for _sub, _label in SUB_LABELS_R_EN.items():
    _n = SUBR_EN.get(_sub, 0) + (1 if (_sub == "serwis" and wax_cross_card_en) else 0)
    if _n:
        cycling_filters_en.append(f"""<button class="filter-btn" onclick="setSub('{_sub}', this)">{_label} ({_n})</button>""")

CYCLING_INDEX_EN = f"""
<h1>🚲 Cycling Reference – Tyre Pressure Calculator and Tables</h1>
<div class="timer-box" style="text-align:left;">
    <h2 style="margin-top:0;">Starting tyre pressure calculator (gravel / MTB / road)</h2>
    <p style="font-size:0.9rem;">Gives an approximate starting point based on the <strong>total system weight</strong> and the tyre width.</p>
    <label for="weight">Total system weight: rider + bike + gear (40 – 170 kg):</label>
    <input type="text" inputmode="decimal" id="weight" value="105">
    <label for="width">Actual tyre width (mm):</label>
    <select id="width">
        <option value="25">25 mm (Road 700×25c / 25-622)</option>
        <option value="28">28 mm (Road 700×28c / 28-622)</option>
        <option value="32">32 mm (Road Plus 700×32c / 32-622)</option>
        <option value="35">35 mm (Gravel 700×35c / 35-622)</option>
        <option value="40" selected>40 mm (Gravel 700×40c / 40-622)</option>
        <option value="45">45 mm (Gravel 700×45c / 45-622)</option>
        <option value="50">50 mm (Monstercross / MTB 29×2.0 / 50-622)</option>
        <option value="57">57 mm (MTB 29×2.25 / 57-622)</option>
    </select>
    <label for="setup">Setup and rim type:</label>
    <select id="setup">
        <option value="tube">Inner tube (standard hooked rim)</option>
        <option value="tubeless_hooked">Tubeless with sealant (hooked rim)</option>
        <option value="tubeless_hookless">Tubeless on a hookless rim (HOOKLESS – 5.0 bar limit!)</option>
    </select>
    <button onclick="calcPressure()">Calculate starting pressure</button>
    <div id="calcWarn" class="alert-box alert-danger" style="display:none; margin-top:1rem;"></div>
    <div id="res" class="param-box" style="margin-top:1rem;" aria-live="polite">
        <div class="param-item"><div class="label">Front (starting)</div><div class="val" id="pFront">2.5 bar</div></div>
        <div class="param-item"><div class="label">Rear (starting)</div><div class="val" id="pRear">2.7 bar</div></div>
    </div>
    <p style="font-size:0.82rem; margin-top:0.5rem; margin-bottom:0;"><strong>Method and limits:</strong> the calculator assumes a weight split of about 46% front / 54% rear and a tyre-volume factor. For hookless rims it automatically caps the result at <strong>5.0 bar (72.5 PSI)</strong>. Always check the allowed pressure on the tyre sidewall and the rim.</p>
</div>

<h2>All cycling tables and tips</h2>
<div class="filter-bar" role="group" aria-label="Cycling sub-category filter">
    {chr(10).join(cycling_filters_en)}
</div>
<label for="q">Search cycling:</label>
<input type="text" id="q" placeholder="🔍 e.g. 40c, 40-622, sealant, wax, torque Nm..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(cycling_cards_en) + wax_cross_card_en}
</div>
<div id="noRes" class="no-results">No matching cycling items.</div>
<script>
function calcPressure() {{
    const rawW = document.getElementById('weight').value.replace(',', '.');
    let w = parseFloat(rawW);
    const warnEl = document.getElementById('calcWarn');
    warnEl.style.display = 'none';

    if (isNaN(w) || w < 40 || w > 170) {{
        warnEl.textContent = "⚠️ Enter a valid total system weight (rider + bike + gear) between 40 and 170 kg.";
        warnEl.style.display = 'block';
        w = Math.min(170, Math.max(40, isNaN(w) ? 95 : w));
        document.getElementById('weight').value = w;
    }}

    const width = parseFloat(document.getElementById('width').value) || 40;
    const setup = document.getElementById('setup').value;
    const isTl = setup.startsWith('tubeless');
    const isHookless = (setup === 'tubeless_hookless');

    let base = (w / (width * 1.48));
    if (width <= 32) base *= 1.95;
    if (isTl) base *= 0.88;

    let front = Math.max(1.1, (base * 0.94));
    let rear = Math.max(1.2, (base * 1.03));

    if (isHookless) {{
        if (width < 28) {{
            warnEl.innerHTML = "🚨 <strong>WARNING (hookless):</strong> most hookless rim makers do not allow tyres narrower than 28 mm (700×28c)! Check your wheel maker's compatibility chart. Maximum pressure has been capped at 5.0 bar.";
            warnEl.style.display = 'block';
        }} else if (front > 5.0 || rear > 5.0) {{
            warnEl.innerHTML = "⚠️ <strong>Hookless limit (5.0 bar):</strong> the calculated pressure exceeded the limit for hookless rims. The value has been capped at 5.0 bar (72.5 PSI)!";
            warnEl.style.display = 'block';
        }}
        front = Math.min(5.0, front);
        rear = Math.min(5.0, rear);
    }}

    const psi = (b) => Math.round(b * 14.5038);
    document.getElementById('pFront').textContent = front.toFixed(1) + " bar (" + psi(front) + " PSI)";
    document.getElementById('pRear').textContent = rear.toFixed(1) + " bar (" + psi(rear) + " PSI)";
}}
calcPressure();
</script>
{FILTER_JS_EN}
"""
save_file("en/cycling/index.html", wrap_html("Tyre Pressure Calculator and Cycling Tables", "Calculate starting tyre pressure for gravel, MTB and road tyres, with hookless limits and total system weight.", CYCLING_INDEX_EN, "en/cycling/", lang="en"))

# 11c. Kitchen (EN) – kopia sekcji 6 z angielskimi tekstami
kitchen_cards_en = []
for slug, _title_pl, temp, mins, _tip_pl in KUCHNIA_ITEMS:
    if slug not in KITCHEN_EN:
        continue
    en_slug, title, tip = KITCHEN_EN[slug]
    rel_url = f"en/kitchen/{en_slug}.html"
    all_urls.append(f"{DOMAIN}/{rel_url}")
    kitchen_cards_en.append(f'<a href="/{rel_url}" class="card" data-sub="airfryer"><span class="badge">🍳 Air fryer</span><h3>{title}</h3><p class="card-val">🌡️ {temp}°C  |  ⏱️ ~{mins} min</p></a>')
    
    is_meat = any(k in slug for k in ["kurczak", "udka", "skrzydelka", "nuggetsy", "karkowka", "schabowy", "mielone", "stek", "burger", "losos", "dorsz"])
    safety_banner = ""
    if is_meat:
        safety_banner = """<div class="alert-box alert-danger"><strong>🌡️ Food safety:</strong> the time is only approximate and depends on the thickness of the portion and the starting temperature of the meat. For poultry always check doneness with a kitchen thermometer in the thickest part – the safe internal temperature is <strong>at least 74°C (165°F)</strong>.</div>"""

    related_html = related_table(
        [(f"/en/kitchen/{KITCHEN_EN[x[0]][0]}.html", KITCHEN_EN[x[0]][1], f"{x[2]}°C · ~{x[3]} min") for x in KUCHNIA_ITEMS if x[0] in KITCHEN_EN and _is_meat(x[0]) == _is_meat(slug)],
        f"/{rel_url}", "Meat and fish in the air fryer – overview" if _is_meat(slug) else "Vegetables, snacks and more – overview", "Food", "Temp · time")
    body = f"""
    <div class="breadcrumbs"><a href="/en/">Home</a> » <a href="/en/kitchen/">Kitchen</a> » {title}</div>
    <h1>{title} – Time and Temperature</h1>
    <p>A starting point for air fryers. Adjust the time to the portion size and the power of your appliance.</p>
    {safety_banner}
    <div class="param-box">
        <div class="param-item"><div class="label">Starting temperature</div><div class="val">{temp}°C <small style="font-size:0.55em; color:var(--muted);">({round(temp * 9 / 5 + 32)}°F)</small></div></div>
        <div class="param-item"><div class="label">Approximate time</div><div class="val">~{mins} min</div></div>
    </div>
    <div class="timer-box">
        <div class="wakelock-status" id="wlStatus">ℹ️ Screen wake lock: off (turns on when you press Start)</div>
        <div class="timer-display" id="timer" aria-live="polite">{mins:02d}:00</div>
        <div>
            <button id="startBtn" onclick="toggleTimer({mins*60})">▶ Start</button>
            <button class="btn-secondary" onclick="resetTimer({mins*60})">↺ Reset</button>
        </div>
    </div>
    <h2>💡 Preparation and tips</h2>
    <div class="info-box"><p>{tip}</p></div>
    <h2>How to check doneness</h2>
    <div class="info-box">
        <ul>
            <li><strong>Basket loading:</strong> the time assumes a single layer with hot air flowing freely. With a full basket add 20–30% to the time and shake the contents.</li>
            <li><strong>Starting state:</strong> food straight from the freezer or very thick pieces need longer to cook through.</li>
            <li><strong>Check before the end:</strong> look into the drawer 2–3 minutes before the time is up, and use a probe thermometer for meat and poultry.</li>
        </ul>
    </div>
    {related_html}
    <p style="margin-top:1.5rem;"><a href="/en/kitchen/" class="btn">← Back to the full air fryer table</a></p>
    <script>
    let interval = null, wakeLock = null, timeLeft = {mins*60}, isRunning = false;
    const wlEl = document.getElementById('wlStatus');
    const timerEl = document.getElementById('timer');
    const startBtn = document.getElementById('startBtn');

    async function requestWakeLock() {{
        if (!('wakeLock' in navigator)) {{
            wlEl.textContent = "⚠️ Your browser doesn't support screen wake lock – the screen may turn off.";
            return;
        }}
        try {{
            wakeLock = await navigator.wakeLock.request('screen');
            wlEl.textContent = "🔒 Screen wake lock: ON";
            wlEl.style.color = "#10b981";
            wakeLock.addEventListener('release', () => {{
                if (isRunning) {{
                    wlEl.textContent = "⚠️ Screen wake lock was released (e.g. you switched tabs).";
                    wlEl.style.color = "#f59e0b";
                }}
            }});
        }} catch (err) {{
            wlEl.textContent = "⚠️ Couldn't keep the screen on (" + err.name + ").";
            wlEl.style.color = "#f59e0b";
        }}
    }}

    function releaseWakeLock() {{
        if (wakeLock !== null) {{
            wakeLock.release().catch(() => {{}});
            wakeLock = null;
        }}
        wlEl.textContent = "ℹ️ Screen wake lock: off";
        wlEl.style.color = "";
    }}

    document.addEventListener('visibilitychange', () => {{
        if (wakeLock !== null && document.visibilityState === 'visible' && isRunning) {{
            requestWakeLock();
        }}
    }});

    function playBeep() {{
        try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            [0, 0.3, 0.6].forEach(delay => {{
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, ctx.currentTime + delay);
                gain.gain.setValueAtTime(0.25, ctx.currentTime + delay);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(ctx.currentTime + delay);
                osc.stop(ctx.currentTime + delay + 0.2);
            }});
        }} catch(e) {{}}
    }}

    function updateDisplay() {{
        const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
        const s = String(timeLeft % 60).padStart(2, '0');
        timerEl.textContent = m + ":" + s;
    }}

    function toggleTimer(defaultSec) {{
        if (isRunning) {{
            clearInterval(interval);
            isRunning = false;
            startBtn.textContent = "▶ Resume";
            releaseWakeLock();
            return;
        }}
        if (timeLeft <= 0) timeLeft = defaultSec;
        isRunning = true;
        startBtn.textContent = "⏸ Pause";
        requestWakeLock();
        interval = setInterval(() => {{
            timeLeft--;
            if (timeLeft <= 0) {{
                clearInterval(interval);
                isRunning = false;
                timerEl.textContent = "DONE! 🔔";
                startBtn.textContent = "▶ Start";
                releaseWakeLock();
                playBeep();
                return;
            }}
            updateDisplay();
        }}, 1000);
    }}

    function resetTimer(defaultSec) {{
        clearInterval(interval);
        isRunning = false;
        timeLeft = defaultSec;
        updateDisplay();
        startBtn.textContent = "▶ Start";
        releaseWakeLock();
    }}
    </script>
    """
    save_file(rel_url, wrap_html(title, f"{title}: approximate temperature ({temp}°C / {round(temp * 9 / 5 + 32)}°F), time (~{mins} min), safety tips and an online timer.", body, rel_url, lang="en"))


# 11d. Checklists (EN) – kopia sekcji 9 z angielskimi tekstami
lists_cards_en = []
for slug, *_pl in LISTY_ITEMS:
    if slug not in LISTS_EN:
        continue
    en_slug, title, badge_cat, desc, groups = LISTS_EN[slug]
    rel_url = f"en/checklists/{en_slug}.html"
    all_urls.append(f"{DOMAIN}/{rel_url}")
    total_items = sum(len(items) for _, items in groups)
    lists_cards_en.append(f'<a href="/{rel_url}" class="card" data-sub="checklista"><span class="badge">{badge_cat}</span><h3>{title}</h3><p class="card-val">☑️ {total_items} items  |  🖨️ Print A4 / PDF</p></a>')

    groups_html = ""
    item_idx = 0
    for g_title, g_items in groups:
        lis = ""
        for it in g_items:
            lis += f'<li class="item-row" data-idx="{item_idx}"><input type="checkbox"><span>{it}</span></li>\n'
            item_idx += 1
        groups_html += f"""
        <div class="checklist-group">
            <div class="group-title">{g_title}</div>
            <ul class="item-list">
                {lis}
            </ul>
        </div>"""

    related_html = related_table(
        [(f"/en/checklists/{v[0]}.html", v[1], sum(len(i) for _, i in v[4])) for v in LISTS_EN.values() if _badge_group(v[2]) == _badge_group(badge_cat)],
        f"/{rel_url}", f"Similar checklists: {_badge_group(badge_cat)}", "List", "Items")
    body = f"""
    <div class="breadcrumbs"><a href="/en/">Home</a> » <a href="/en/checklists/">Checklists</a> » {title}</div>
    <h1>{title}</h1>
    <p>{desc} Tick things off as you pack – the list is saved automatically on your device. You can also add your own items, print a clean A4 sheet or send the current state to family as a link.</p>

    <div class="checklist-action-bar">
        <div style="flex: 1 1 200px;">
            <strong id="counter" style="color:var(--accent); font-size:1.05rem;">Done: 0 / {total_items} (0%)</strong>
            <div class="progress-wrap"><div class="progress-bar" id="progBar"></div></div>
        </div>
        <div style="display:flex; gap:0.35rem; flex-wrap:wrap;">
            <button onclick="window.print()">🖨️ Print / PDF</button>
            <button class="btn-secondary" onclick="shareUrl()" id="shareBtn">🔗 Share progress</button>
            <button class="btn-secondary" onclick="sendViaEmail()">✉️ Send by email</button>
            <button class="btn-secondary" onclick="resetList()">↺ Clear</button>
        </div>
    </div>

    {groups_html}

    <div class="checklist-group">
        <div class="group-title">➕ Your own items (added to the list)</div>
        <div class="add-custom-box">
            <input type="text" id="customInput" placeholder="Add your own item (e.g. favourite teddy, watch charger)..." onkeydown="if(event.key==='Enter') addCustomItem()">
            <button onclick="addCustomItem()" style="white-space:nowrap;">+ Add item</button>
        </div>
        <ul class="item-list" id="customList"></ul>
    </div>

    {related_html}
    <p style="margin-top:2rem;"><a href="/en/checklists/" class="btn">← See all checklists</a></p>

    <script>
    const STORAGE_KEY = "mn_list_en_{en_slug}_v1";

    function getStored() {{
        try {{
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {{ checked: [], custom: [], customChecked: [] }};
        }} catch(e) {{
            return {{ checked: [], custom: [], customChecked: [] }};
        }}
    }}

    function saveStored(data) {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }}

    function updateStats() {{
        const allRows = document.querySelectorAll('.item-row');
        const checkedRows = document.querySelectorAll('.item-row.checked');
        const total = allRows.length;
        const done = checkedRows.length;
        const pct = total > 0 ? Math.round((done / total) * 100) : 0;
        document.getElementById('counter').textContent = `Packed / done: ${{done}} / ${{total}} (${{pct}}%)`;
        document.getElementById('progBar').style.width = pct + "%";
    }}

    function syncToStorage() {{
        const data = getStored();
        const checkedIdx = [];
        document.querySelectorAll('.item-row[data-idx]').forEach(row => {{
            if (row.classList.contains('checked')) {{
                checkedIdx.push(parseInt(row.getAttribute('data-idx'), 10));
            }}
        }});
        const customChecked = [];
        document.querySelectorAll('#customList .item-row').forEach(row => {{
            if (row.classList.contains('checked')) {{
                customChecked.push(row.getAttribute('data-custom'));
            }}
        }});
        data.checked = checkedIdx;
        data.customChecked = customChecked;
        saveStored(data);
        updateStats();
    }}

    function bindRowEvents(row) {{
        const cb = row.querySelector('input[type="checkbox"]');
        row.addEventListener('click', (e) => {{
            if (e.target.tagName === 'SMALL') return;
            if (e.target !== cb) cb.checked = !cb.checked;
            if (cb.checked) row.classList.add('checked');
            else row.classList.remove('checked');
            syncToStorage();
        }});
    }}

    function renderCustomItem(text, isChecked) {{
        const ul = document.getElementById('customList');
        const li = document.createElement('li');
        li.className = 'item-row' + (isChecked ? ' checked' : '');
        li.setAttribute('data-custom', text);
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = isChecked;
        const span = document.createElement('span');
        span.textContent = text;
        const delBtn = document.createElement('small');
        delBtn.textContent = '✖ Remove';
        delBtn.style.cssText = 'margin-left:auto; color:var(--danger); cursor:pointer; font-weight:700; padding:0.2rem 0.4rem;';
        delBtn.onclick = (e) => {{
            e.stopPropagation();
            const d = getStored();
            d.custom = (d.custom || []).filter(t => t !== text);
            d.customChecked = (d.customChecked || []).filter(t => t !== text);
            saveStored(d);
            li.remove();
            updateStats();
        }};
        li.appendChild(cb);
        li.appendChild(span);
        li.appendChild(delBtn);
        ul.appendChild(li);
        bindRowEvents(li);
    }}

    function addCustomItem() {{
        const inp = document.getElementById('customInput');
        const val = inp.value.trim();
        if (!val) return;
        const data = getStored();
        if (!data.custom) data.custom = [];
        if (!data.custom.includes(val)) {{
            data.custom.push(val);
            saveStored(data);
            renderCustomItem(val, false);
            inp.value = "";
            updateStats();
        }}
    }}

    function initChecklist() {{
        let data = getStored();
        const params = new URLSearchParams(window.location.search);
        if (params.has('c')) {{
            const fromUrl = params.get('c').split(',').map(x => parseInt(x, 10)).filter(x => !isNaN(x));
            data.checked = fromUrl;
            if (params.has('add')) {{
                const added = params.get('add').split('|').map(s => s.trim()).filter(Boolean);
                added.forEach(item => {{
                    if (!data.custom.includes(item)) data.custom.push(item);
                }});
            }}
            saveStored(data);
        }}

        document.querySelectorAll('.item-row[data-idx]').forEach(row => {{
            const idx = parseInt(row.getAttribute('data-idx'), 10);
            const cb = row.querySelector('input[type="checkbox"]');
            if ((data.checked || []).includes(idx)) {{
                cb.checked = true;
                row.classList.add('checked');
            }}
            bindRowEvents(row);
        }});

        (data.custom || []).forEach(txt => {{
            const isC = (data.customChecked || []).includes(txt);
            renderCustomItem(txt, isC);
        }});

        updateStats();
    }}

    function shareUrl() {{
        const data = getStored();
        const url = new URL(window.location.origin + window.location.pathname);
        if (data.checked && data.checked.length > 0) {{
            url.searchParams.set('c', data.checked.join(','));
        }}
        if (data.custom && data.custom.length > 0) {{
            url.searchParams.set('add', data.custom.join('|'));
        }}
        const shareLink = url.toString();
        if (navigator.clipboard) {{
            navigator.clipboard.writeText(shareLink).then(() => {{
                const btn = document.getElementById('shareBtn');
                btn.textContent = "✅ Link copied!";
                setTimeout(() => {{ btn.textContent = "🔗 Share progress"; }}, 2500);
            }});
        }} else {{
            prompt("Copy this link with the state of your list:", shareLink);
        }}
    }}

    function sendViaEmail() {{
        let body = "{title} (My Toolbelt – mojniezbednik.pl):\\n\\n";
        document.querySelectorAll('.checklist-group').forEach(grp => {{
            const gTitle = grp.querySelector('.group-title').textContent.trim();
            const rows = grp.querySelectorAll('.item-row');
            if (rows.length > 0) {{
                body += "=== " + gTitle + " ===\\n";
                rows.forEach(r => {{
                    const mark = r.classList.contains('checked') ? "[X]" : "[ ]";
                    const txt = r.querySelector('span').textContent.trim();
                    body += `${{mark}} ${{txt}}\\n`;
                }});
                body += "\\n";
            }}
        }});
        body += "Link to the interactive list: " + window.location.href;
        window.location.href = `mailto:?subject=${{encodeURIComponent("{title}")}}&body=${{encodeURIComponent(body)}}`;
    }}

    function resetList() {{
        if (confirm("Are you sure you want to untick all items on this list?")) {{
            const data = getStored();
            data.checked = [];
            data.customChecked = [];
            saveStored(data);
            document.querySelectorAll('.item-row').forEach(r => {{
                r.classList.remove('checked');
                r.querySelector('input[type="checkbox"]').checked = false;
            }});
            if (window.history.replaceState) {{
                window.history.replaceState(null, null, window.location.pathname);
            }}
            updateStats();
        }}
    }}

    initChecklist();
    </script>
    """
    save_file(rel_url, wrap_html(title, f"{title} – interactive checklist that saves your progress, prints on A4/PDF and can be sent by email.", body, rel_url, lang="en"))



KITCHEN_INDEX_EN = f"""
<h1>🍳 Kitchen Reference – Air Fryer Times and Temperatures</h1>
<p>Type a food below to filter the list:</p>
<div class="alert-box"><strong>Tip:</strong> all times are approximate for a single layer in the basket. When cooking poultry, always check the internal temperature with a thermometer (at least 74°C / 165°F).</div>
<label for="q">Search for a food:</label>
<input type="text" id="q" placeholder="🔍 e.g. fries, chicken, salmon, eggs..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(kitchen_cards_en)}
</div>
<div id="noRes" class="no-results">No matching items. Try a different word.</div>
{FILTER_JS_EN}
"""
all_urls.append(f"{DOMAIN}/en/kitchen/")
save_file("en/kitchen/index.html", wrap_html("Air Fryer Cooking Times and Temperatures Chart", "Approximate air fryer cooking times and temperatures with a built-in timer and doneness checks.", KITCHEN_INDEX_EN, "en/kitchen/", lang="en"))

CHECKLISTS_INDEX_EN = f"""
<h1>🎒 Packing Lists and Checklists – Printable and Interactive</h1>
<p>Tick items off on your phone (your progress is saved on the device), add your own items, print on A4 or send the list by email. Type below to filter:</p>
<label for="q">Search the lists:</label>
<input type="text" id="q" placeholder="🔍 e.g. camp, ski, camping, carry-on, hospital, bikepacking..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(lists_cards_en)}
</div>
<div id="noRes" class="no-results">No matching checklist.</div>
{FILTER_JS_EN}
"""
all_urls.append(f"{DOMAIN}/en/checklists/")
save_file("en/checklists/index.html", wrap_html("Packing Lists for Trips, Camping and Hobbies – Printable Checklists", "Interactive checklists to tick off on your phone and print on A4/PDF: summer camp, ski trip, camping, carry-on luggage, hospital bag, bikepacking and more.", CHECKLISTS_INDEX_EN, "en/checklists/", lang="en"))

HOME_BODY_EN = f"""
<h1>⚡ My Toolbelt – No-Fluff Calculators, Tables and Checklists</h1>
<p>Quick reference tables and starting parameters with their conditions of use – without endless introductions. Choose a section or search below:</p>
<div class="grid" style="margin-bottom:2rem;">
    <a href="/en/checklists/" class="card cat-card" style="border-color:var(--accent);">
        <span class="badge">{N_LIST_EN} interactive checklists</span>
        <h3>{ICON['lists']}Packing Lists &amp; Checklists</h3>
        <p>Summer camp, ski trip, camping, carry-on, bikepacking, hospital bag (print A4 / PDF)</p>
    </a>
    <a href="/en/kitchen/" class="card cat-card">
        <span class="badge">{N_KUCH_EN} items</span>
        <h3>{ICON['kitchen']}Kitchen &amp; Air Fryer</h3>
        <p>Approximate times, food-safety temperatures (74°C / 165°F for poultry) + a timer that keeps the screen on</p>
    </a>
    <a href="/en/workshop/" class="card cat-card">
        <span class="badge">{N_WARS_EN} items + calculators</span>
        <h3>{ICON['workshop']}Workshop, Renovation &amp; DIY</h3>
        <p>Paint and concrete calculators, tap drill sizes M2–M20, steel heat treatment, 3D printing temperatures</p>
    </a>
    <a href="/en/cycling/" class="card cat-card">
        <span class="badge">{N_ROW_EN} items + calculator</span>
        <h3>{ICON['bike']}Cycling &amp; Bike Service</h3>
        <p>Tyre pressure calculator (hooked / hookless), tubeless sealant amounts, torque specs</p>
    </a>
</div>

<h2>🔍 Search all {N_LIST_EN + N_KUCH_EN + N_WARS_EN + N_ROW_EN} tools, tables and lists</h2>
<label for="q">Type what you're looking for (e.g. paint, concrete, m8, fries, chicken, camping, 40c):</label>
<input type="text" id="q" placeholder="Search e.g. paint, M8, fries, camping, 40c..." oninput="filterCards()">
<div class="grid" id="cards">
{''.join(lists_cards_en + kitchen_cards_en + workshop_cards_en + cycling_cards_en)}
</div>
<div id="noRes" class="no-results">No matching tool found. Check the spelling or go straight to a section above.</div>
<script>
function filterCards() {{
    const q = normStr(document.getElementById('q').value);
    let visible = 0;
    document.querySelectorAll('#cards .card').forEach(c => {{
        const show = normStr(c.textContent).includes(q);
        c.style.display = show ? 'flex' : 'none';
        if (show) visible++;
    }});
    document.getElementById('noRes').style.display = visible === 0 ? 'block' : 'none';
}}
</script>
"""
all_urls.append(f"{DOMAIN}/en/")
all_urls.append(f"{DOMAIN}/en/workshop/")
all_urls.append(f"{DOMAIN}/en/cycling/")
save_file("en/index.html", wrap_html("Quick Calculators, Packing Lists, Air Fryer Times and Workshop Tables", "No-fluff toolbelt: packing checklists for camp and travel, air fryer times, paint and concrete calculators, tap drill sizes and a bike tyre pressure calculator.", HOME_BODY_EN, "en/", lang="en"))

# 12. Strona 404, sitemap.xml (z prawdziwymi datami zmian) oraz robots.txt
NOT_FOUND_BODY = f"""
<h1>404 – Nie ma takiej strony</h1>
<p>Ten adres nie istnieje albo został zmieniony. Wybierz dział lub skorzystaj z wyszukiwarki na stronie głównej.</p>
<div class="grid" style="margin-top:1.5rem;">
    <a href="/" class="card"><h3>⚡ Strona główna i wyszukiwarka</h3></a>
    <a href="/listy/" class="card cat-card"><h3>{ICON['lists']}Listy i Niezbędniki</h3></a>
    <a href="/kuchnia/" class="card cat-card"><h3>{ICON['kitchen']}Kuchnia & Airfryer</h3></a>
    <a href="/warsztat/" class="card cat-card"><h3>{ICON['workshop']}Warsztat, Remont & DIY</h3></a>
    <a href="/rower/" class="card cat-card"><h3>{ICON['bike']}Rower & Serwis</h3></a>
</div>
"""
save_file("404.html", wrap_html("Nie znaleziono strony (404)", "Ta strona nie istnieje. Przejdź do działów MójNiezbędnik.pl.", NOT_FOUND_BODY, noindex=True))

def _lastmod_for(url):
    rel = url[len(DOMAIN):].lstrip("/")
    file_rel = rel + "index.html" if (rel == "" or rel.endswith("/")) else rel
    return BUILD_STATE.get(file_rel, {}).get("lastmod", TODAY)

sitemap_entries = "\n".join([f"  <url><loc>{u}</loc><lastmod>{_lastmod_for(u)}</lastmod></url>" for u in all_urls])
SITEMAP_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_entries}
</urlset>"""
save_file("sitemap.xml", SITEMAP_XML)

ROBOTS_TXT = f"""User-agent: *
Allow: /
Sitemap: {DOMAIN}/sitemap.xml
"""
save_file("robots.txt", ROBOTS_TXT)

# 13. Pliki statyczne z repozytorium: favicon, ikona na ekran główny, obrazek do udostępniania
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
if os.path.isdir(STATIC_DIR):
    for name in sorted(os.listdir(STATIC_DIR)):
        src = os.path.join(STATIC_DIR, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(BASE_DIR, name))

# 14. Zapis stanu (daty zmian stron) na następne uruchomienie
try:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(BUILD_STATE, f, ensure_ascii=False, indent=0, sort_keys=True)
except OSError as e:
    print(f"Uwaga: nie zapisano {STATE_FILE}: {e}")

print(f"✅ GOTOWE! Wygenerowano łącznie {len(all_urls)} adresów URL w {BASE_DIR}")
