#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import date

BASE_DIR = "/var/www/hub"
DOMAIN = "https://mojniezbednik.pl"
TODAY = date.today().isoformat()

# 1. Tworzenie katalogów
for sub in ["", "kuchnia", "warsztat", "rower", "listy"]:
    os.makedirs(os.path.join(BASE_DIR, sub), exist_ok=True)

def save_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

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
    background: rgba(255,255,255,0.04);
    white-space: nowrap;
}
nav a:hover { color: var(--accent); background: rgba(255,255,255,0.08); }
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
.lang-btn:hover { background: var(--accent); color: #000; }
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
}
.card h3 { font-size: 1.1rem; margin-bottom: 0.5rem; color: var(--text); line-height: 1.35; }
.card .card-val {
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
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
    color: #000;
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
.btn-secondary { background: #334155; color: var(--text); }
.btn-secondary:hover { background: #475569; }
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
    color: #000;
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
    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
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
    header, footer, .checklist-action-bar, .add-custom-box, .breadcrumbs, .btn, button, .alert-box { display: none !important; }
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

# 3. Wspólny szablon HTML ze słownikiem PL/EN (My Toolbelt)
def wrap_html(title, desc, body, canonical_path=""):
    canonical_url = f"{DOMAIN}/{canonical_path}".rstrip("/")
    if canonical_path == "":
        canonical_url = f"{DOMAIN}/"

    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Mój Niezbędnik / My Toolbelt</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{canonical_url}">
    <link rel="stylesheet" href="/style.css">
</head>
<body>
<header>
    <div class="nav-container">
        <a href="/" class="logo" id="siteLogo">⚡ MójNiezbędnik.pl</a>
        <nav aria-label="Główna nawigacja">
            <a href="/kuchnia/" data-i18n="nav_kitchen">🍳 Kuchnia (38)</a>
            <a href="/warsztat/" data-i18n="nav_workshop">🔧 Warsztat (38)</a>
            <a href="/rower/" data-i18n="nav_bike">🚲 Rower (26)</a>
            <a href="/listy/" data-i18n="nav_lists">🎒 Listy (12)</a>
            <button class="lang-btn" id="langToggleBtn" onclick="toggleLanguage()" title="Switch language PL/EN">🇬🇧 EN</button>
        </nav>
    </div>
</header>
<main>
{body}
</main>
<footer>
    <div class="footer-grid">
        <div>
            <h4 data-i18n="foot_about_h">O projekcie MójNiezbędnik.pl</h4>
            <p data-i18n="foot_about_p">Zbiór praktycznych tabel, punktów startowych, kalkulatorów oraz interaktywnych list pakowania (checklist). Ostatnia aktualizacja: <strong>{TODAY}</strong>.</p>
        </div>
        <div>
            <h4 data-i18n="foot_safe_h">Metodologia i bezpieczeństwo</h4>
            <p data-i18n="foot_safe_p">Podane wartości mają charakter orientacyjny (punkty wyjścia). Przed wykonaniem prac elektrycznych, obróbki cieplnej czy montażu komponentów rowerowych zawsze sprawdź dokumentację producenta i normy branżowe.</p>
        </div>
        <div>
            <h4 data-i18n="foot_contact_h">Kontakt i zgłaszanie uwag</h4>
            <p><span data-i18n="foot_contact_p">Znalazłeś błąd w tabeli lub chcesz zasugerować nową listę? Napisz:</span> <a href="mailto:kontakt@mojniezbednik.pl" style="color:var(--accent);">kontakt@mojniezbednik.pl</a></p>
        </div>
    </div>
    <p style="text-align:center; border-top:1px solid var(--border); padding-top:1rem;" data-i18n="foot_copy">© {TODAY[:4]} MójNiezbędnik.pl (My Toolbelt) – Brak ciasteczek śledzących. Zaznaczenia list zapisywane są lokalnie na Twoim urządzeniu.</p>
</footer>
<script>
function normStr(s) {{
    return (s || "").toLowerCase()
        .normalize("NFD").replace(/[\\u0300-\\u036f]/g, "")
        .replace(/ł/g, "l")
        .replace(/[-_\\s]+/g, "");
}}

const I18N_DICT = {{
    pl: {{
        logo: "⚡ MójNiezbędnik.pl",
        nav_kitchen: "🍳 Kuchnia (38)",
        nav_workshop: "🔧 Warsztat (38)",
        nav_bike: "🚲 Rower (26)",
        nav_lists: "🎒 Listy (12)",
        foot_about_h: "O projekcie MójNiezbędnik.pl",
        foot_about_p: "Zbiór praktycznych tabel, punktów startowych, kalkulatorów oraz interaktywnych list pakowania (checklist). Ostatnia aktualizacja: {TODAY}.",
        foot_safe_h: "Metodologia i bezpieczeństwo",
        foot_safe_p: "Podane wartości mają charakter orientacyjny (punkty wyjścia). Przed wykonaniem prac elektrycznych, obróbki cieplnej czy montażu komponentów rowerowych zawsze sprawdź dokumentację producenta i normy branżowe.",
        foot_contact_h: "Kontakt i zgłaszanie uwag",
        foot_contact_p: "Znalazłeś błąd w tabeli lub chcesz zasugerować nową listę? Napisz:",
        foot_copy: "© {TODAY[:4]} MójNiezbędnik.pl – Brak ciasteczek śledzących. Zaznaczenia list zapisywane są lokalnie na Twoim urządzeniu.",
        home_h1: "⚡ MójNiezbędnik.pl – Praktyczne parametry, tabele i interaktywne listy",
        home_sub: "Szybkie punkty wyjścia z podanymi warunkami oraz interaktywne checklisty do druku – bez zbędnych wstępów. Wybierz dział lub wyszukaj narzędzie poniżej:",
        cat_lists_b: "12 interaktywnych list",
        cat_lists_h: "🎒 Listy i Niezbędniki",
        cat_lists_p: "Co zabrać na obóz, kolonie, zimowisko, biwak, bikepacking i do szpitala (Druk A4 / PDF)",
        cat_kitch_b: "38 pozycji",
        cat_kitch_h: "🍳 Kuchnia & Airfryer",
        cat_kitch_p: "Orientacyjne czasy, kryteria temperatury (74°C dla drobiu) + minutnik z Wake Lock",
        cat_work_b: "38 pozycji + Kalkulatory",
        cat_work_h: "🔧 Warsztat, Remont & DIY",
        cat_work_p: "Kalkulator farby i betonu, wiertła pod gwinty M2–M20, obróbka cieplna stali, druk 3D",
        cat_bike_b: "26 pozycji + Kalkulator",
        cat_bike_h: "🚲 Rower & Serwis",
        cat_bike_p: "Kalkulator ciśnienia (Hooked / Hookless), dawki mleczka tubeless, momenty Nm",
        home_search_h: "🔍 Wyszukiwarka wszystkich 114 narzędzi, kalkulatorów i list",
        home_search_lbl: "Wpisz szukaną frazę (obsługuje zapytania bez polskich znaków i spacji, np. farba, beton, oboz, piers, m 8, 40-622):",
        paint_h2: "🎨 Kalkulator Farby (Ile litrów na pokój / ściany?)",
        paint_desc: "Wpisz łączną powierzchnię do pomalowania, odejmij okna/drzwi i oblicz potrzebną ilość farby wraz z 10% zapasem.",
        paint_area_lbl: "Powierzchnia ścian/sufitu (m²):",
        paint_openings_lbl: "Liczba drzwi i okien (odlicza ~1.8 m²/szt.):",
        paint_layers_lbl: "Liczba warstw malowania:",
        paint_yield_lbl: "Wydajność farby z puszki (m²/L):",
        paint_btn: "Oblicz ilość farby",
        paint_res_net: "Powierzchnia netto (1 warstwa)",
        paint_res_total: "Potrzebna farba (+10% zapasu)",
        mortar_h2: "🧱 Kalkulator Zaprawy i Betonu (Przelicznik na wiadra 10L i worki)",
        mortar_desc: "Praktyczne proporcje budowlane przeliczone na zwykłe wiadra budowlane (10 litrów) i worki cementu (25 kg).",
        mortar_type_lbl: "Wybierz rodzaj mieszanki:",
        mortar_opt_concrete: "Beton roboczy B15/B20 – pod słupki, posadzkę, podmurówkę (1 : 2 : 3)",
        mortar_opt_masonry: "Zaprawa murarska / tynkarska cementowo-wapienna (1 : 1 : 6)",
        mortar_opt_cement: "Zaprawa czysto cementowa – mocna, podkładowa, reperacje (1 : 3)",
        mortar_batches_lbl: "Mnożnik zarobów (1 zarób = na 1 worek cementu 25 kg / ~20L):",
        bike_calc_h2: "Kalkulator ciśnienia startowego w oponach (Gravel / MTB / Szosa)",
        bike_weight_lbl: "Masa całkowita zestawu: kolarz + rower + ekwipunek (40 – 170 kg):",
        bike_width_lbl: "Rzeczywista szerokość opony (mm):",
        bike_setup_lbl: "System montażu i typ obręczy:",
        bike_btn: "Oblicz ciśnienie startowe",
        bike_front: "Przód (Startowe)",
        bike_rear: "Tył (Startowe)"
    }},
    en: {{
        logo: "⚡ My Toolbelt (mojniezbednik.pl)",
        nav_kitchen: "🍳 Kitchen (38)",
        nav_workshop: "🔧 Workshop (38)",
        nav_bike: "🚲 Cycling (26)",
        nav_lists: "🎒 Checklists (12)",
        foot_about_h: "About My Toolbelt (MójNiezbędnik.pl)",
        foot_about_p: "No-fluff collection of practical workshop tables, calculators, airfryer timers, and printable A4 checklists. Last updated: {TODAY}.",
        foot_safe_h: "Methodology & Safety",
        foot_safe_p: "Provided values are starting reference points. Always verify manufacturer documentation and local building/electrical codes before performing work.",
        foot_contact_h: "Contact & Feedback",
        foot_contact_p: "Found an error or want to suggest a new tool? Email us:",
        foot_copy: "© {TODAY[:4]} MójNiezbędnik.pl (My Toolbelt) – Zero tracking cookies. Checklist states are saved locally on your device.",
        home_h1: "⚡ My Toolbelt – No-Fluff Workshop, Kitchen & Cycling Calculators",
        home_sub: "Quick reference tables, starting parameters, and printable checklists without endless SEO stories. Choose a category or search below:",
        cat_lists_b: "12 interactive checklists",
        cat_lists_h: "🎒 Packing Lists & Kits",
        cat_lists_p: "Camping, bikepacking, carry-on luggage, blackout kit, and DIY toolbelt (A4 Print / PDF)",
        cat_kitch_b: "38 items",
        cat_kitch_h: "🍳 Kitchen & Airfryer",
        cat_kitch_p: "Reference cooking times, food safety temps (74°C for poultry) + Wake Lock timer",
        cat_work_b: "38 items + Calculators",
        cat_work_h: "🔧 Workshop, Renovation & DIY",
        cat_work_p: "Paint & concrete calculators, tap drill sizes M2–M20, steel heat treating, 3D printing",
        cat_bike_b: "26 items + Calculator",
        cat_bike_h: "🚲 Cycling & Bike Wrench",
        cat_bike_p: "Tire pressure calculator (Hooked / Hookless), tubeless sealant dosage, torque specs (Nm)",
        home_search_h: "🔍 Search all 114 tools, calculators & checklists",
        home_search_lbl: "Type a keyword (e.g. paint, concrete, m8, 1.2842, petg, 40c, chicken):",
        paint_h2: "🎨 Paint Calculator (How many liters for a room / walls?)",
        paint_desc: "Enter total wall/ceiling area, subtract doors/windows, and calculate required paint volume including a 10% safety margin.",
        paint_area_lbl: "Total wall/ceiling surface area (m²):",
        paint_openings_lbl: "Number of doors & windows (subtracts ~1.8 m² each):",
        paint_layers_lbl: "Number of coats:",
        paint_yield_lbl: "Paint coverage per liter (m²/L):",
        paint_btn: "Calculate paint needed",
        paint_res_net: "Net paintable area (1 coat)",
        paint_res_total: "Paint required (+10% margin)",
        mortar_h2: "🧱 Mortar & Concrete Proportions (10L Bucket & 25kg Bag Scale)",
        mortar_desc: "Practical renovation mix ratios translated into standard 10-liter construction buckets and 25 kg cement bags.",
        mortar_type_lbl: "Select mix type:",
        mortar_opt_concrete: "Standard Concrete (B15/B20) – fence posts, slabs, foundations (1 : 2 : 3)",
        mortar_opt_masonry: "Masonry / Plastering Mortar – cement-lime mix (1 : 1 : 6)",
        mortar_opt_cement: "Pure Cement Mortar – high strength, repairs, screeds (1 : 3)",
        mortar_batches_lbl: "Batch multiplier (1 batch = per one 25 kg cement bag / ~20L):",
        bike_calc_h2: "Starting Tire Pressure Calculator (Gravel / MTB / Road)",
        bike_weight_lbl: "Total system weight: rider + bike + gear (40 – 170 kg):",
        bike_width_lbl: "Actual tire width (mm):",
        bike_setup_lbl: "Mounting system & rim type:",
        bike_btn: "Calculate starting pressure",
        bike_front: "Front (Starting)",
        bike_rear: "Rear (Starting)"
    }}
}};

let currentLang = localStorage.getItem('mn_lang') || 'pl';

function applyLanguage(lang) {{
    currentLang = lang;
    localStorage.setItem('mn_lang', lang);
    document.documentElement.lang = lang;
    const dict = I18N_DICT[lang] || I18N_DICT.pl;
    const logoEl = document.getElementById('siteLogo');
    if (logoEl) logoEl.textContent = dict.logo;
    const btn = document.getElementById('langToggleBtn');
    if (btn) btn.textContent = lang === 'pl' ? '🇬🇧 EN' : '🇵🇱 PL';

    document.querySelectorAll('[data-i18n]').forEach(el => {{
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.textContent = dict[key];
    }});

    if (typeof calcPaint === 'function') calcPaint();
    if (typeof calcMortar === 'function') calcMortar();
    if (typeof applyHomeView === 'function') applyHomeView();
}}

function toggleLanguage() {{
    applyLanguage(currentLang === 'pl' ? 'en' : 'pl');
}}

document.addEventListener('DOMContentLoaded', () => {{
    applyLanguage(currentLang);
}});
</script>
</body>
</html>"""

# 4. Baza danych: Kuchnia (38), Warsztat (36 + 2 kalkulatory = 38), Rower (26), Listy (12)
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
    ("momenty-dokrecania-kaseta-tarcze-centerlock", "Orientacyjne momenty dokręcania: Kaseta i tarcze hamulcowe", "Nakrętka kasety / tarczy Centerlock: 40 Nm", "Tarcza hamulcowa na 6 śrub (Torx T25): 5 – 6 Nm", "Śruby tarczy na 6 śrub dokręcaj kluczem dynamometrycznym w kolejności gwiazdowej (na krzyż).", "serwis"),
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
    <h2 style="margin-top:0;" data-i18n="paint_h2">🎨 Kalkulator Farby (Ile litrów na pokój / ściany?)</h2>
    <p style="font-size:0.9rem;" data-i18n="paint_desc">Wpisz łączną powierzchnię do pomalowania, odejmij okna/drzwi i oblicz potrzebną ilość farby wraz z 10% zapasem.</p>
    <div class="form-row">
        <div>
            <label for="pArea" data-i18n="paint_area_lbl">Powierzchnia ścian/sufitu (m²):</label>
            <input type="number" id="pArea" value="45" min="1" step="1" oninput="calcPaint()">
        </div>
        <div>
            <label for="pOpenings" data-i18n="paint_openings_lbl">Liczba drzwi i okien (odlicza ~1.8 m²/szt.):</label>
            <input type="number" id="pOpenings" value="3" min="0" step="1" oninput="calcPaint()">
        </div>
    </div>
    <div class="form-row">
        <div>
            <label for="pLayers" data-i18n="paint_layers_lbl">Liczba warstw malowania:</label>
            <input type="number" id="pLayers" value="2" min="1" max="5" step="1" oninput="calcPaint()">
        </div>
        <div>
            <label for="pYield" data-i18n="paint_yield_lbl">Wydajność farby z puszki (m²/L):</label>
            <input type="number" id="pYield" value="12" min="1" step="0.5" oninput="calcPaint()">
        </div>
    </div>
    <button onclick="calcPaint()" data-i18n="paint_btn">Oblicz ilość farby</button>
    <div class="param-box" style="margin-top:1rem;" aria-live="polite">
        <div class="param-item"><div class="label" data-i18n="paint_res_net">Powierzchnia netto (1 warstwa)</div><div class="val" id="pNetVal">39.6 m²</div></div>
        <div class="param-item"><div class="label" data-i18n="paint_res_total">Potrzebna farba (+10% zapasu)</div><div class="val" id="pLitresVal">7.3 L</div></div>
    </div>
</div>

<div class="timer-box" style="text-align:left;" id="mortarCalcBox">
    <h2 style="margin-top:0;" data-i18n="mortar_h2">🧱 Kalkulator Zaprawy i Betonu (Przelicznik na wiadra 10L i worki)</h2>
    <p style="font-size:0.9rem;" data-i18n="mortar_desc">Praktyczne proporcje budowlane przeliczone na zwykłe wiadra budowlane (10 litrów) i worki cementu (25 kg).</p>
    <div class="form-row">
        <div>
            <label for="mType" data-i18n="mortar_type_lbl">Wybierz rodzaj mieszanki:</label>
            <select id="mType" onchange="calcMortar()">
                <option value="concrete" data-i18n="mortar_opt_concrete">Beton roboczy B15/B20 – pod słupki, posadzkę, podmurówkę (1 : 2 : 3)</option>
                <option value="masonry" data-i18n="mortar_opt_masonry">Zaprawa murarska / tynkarska cementowo-wapienna (1 : 1 : 6)</option>
                <option value="cement" data-i18n="mortar_opt_cement">Zaprawa czysto cementowa – mocna, podkładowa, reperacje (1 : 3)</option>
            </select>
        </div>
        <div>
            <label for="mBatches" data-i18n="mortar_batches_lbl">Mnożnik zarobów (1 zarób = na 1 worek cementu 25 kg / ~20L):</label>
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
        const yieldL = Math.round(100 * b);
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
        wlEl.style.color = "#cbd5e1";
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
    <button class="filter-btn active" onclick="setSub('all', this)">Wszystkie (38)</button>
    <button class="filter-btn" onclick="setSub('gwinty', this)">🔩 Gwinty (12)</button>
    <button class="filter-btn" onclick="setSub('stal', this)">🔥 Stal i Hartowanie (6)</button>
    <button class="filter-btn" onclick="setSub('druk3d', this)">🖨️ Druk 3D (6)</button>
    <button class="filter-btn" onclick="setSub('elektryka', this)">⚡ Elektryka (6)</button>
    <button class="filter-btn" onclick="setSub('przeliczniki', this)">📐 Budowa i Przeliczniki (8)</button>
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
    <h2 style="margin-top:0;" data-i18n="bike_calc_h2">Kalkulator ciśnienia startowego w oponach (Gravel / MTB / Szosa)</h2>
    <p style="font-size:0.9rem;">Oblicza orientacyjny punkt wyjścia na podstawie <strong>masy całkowitej zestawu</strong> oraz szerokości opony.</p>
    <label for="weight" data-i18n="bike_weight_lbl">Masa całkowita zestawu: kolarz + rower + ekwipunek (40 – 170 kg):</label>
    <input type="text" inputmode="decimal" id="weight" value="105">
    <label for="width" data-i18n="bike_width_lbl">Rzeczywista szerokość opony (mm):</label>
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
    <label for="setup" data-i18n="bike_setup_lbl">System montażu i typ obręczy:</label>
    <select id="setup">
        <option value="tube">Z dętką (obręcz standardowa Hooked)</option>
        <option value="tubeless_hooked">Tubeless z mleczkiem (obręcz z haczykiem Hooked)</option>
        <option value="tubeless_hookless">Tubeless na obręczy bezrantowej (HOOKLESS – limit 5.0 bar!)</option>
    </select>
    <button onclick="calcPressure()" data-i18n="bike_btn">Oblicz ciśnienie startowe</button>
    <div id="calcWarn" class="alert-box alert-danger" style="display:none; margin-top:1rem;"></div>
    <div id="res" class="param-box" style="margin-top:1rem;" aria-live="polite">
        <div class="param-item"><div class="label" data-i18n="bike_front">Przód (Startowe)</div><div class="val" id="pFront">2.5 bar</div></div>
        <div class="param-item"><div class="label" data-i18n="bike_rear">Tył (Startowe)</div><div class="val" id="pRear">2.7 bar</div></div>
    </div>
    <p style="font-size:0.82rem; margin-top:0.5rem; margin-bottom:0;"><strong>Metoda i limity:</strong> Kalkulator przyjmuje rozkład masy ok. 46% przód / 54% tył oraz współczynnik objętości opony. Dla systemu Hookless automatycznie wymusza górny limit bezpieczeństwa <strong>5.0 bar (72.5 PSI)</strong>. Zawsze sprawdź dopuszczalne ciśnienie na ściance opony i obręczy.</p>
</div>

<h2>Wszystkie ściągi i tabele rowerowe</h2>
<div class="filter-bar" role="group" aria-label="Filtr podkategorii rowerowych">
    <button class="filter-btn active" onclick="setSub('all', this)">Wszystkie (27)</button>
    <button class="filter-btn" onclick="setSub('opony', this)">🛞 Opony i Mleczko (18)</button>
    <button class="filter-btn" onclick="setSub('serwis', this)">🔧 Montaż i Napęd (5)</button>
    <button class="filter-btn" onclick="setSub('dopasowanie', this)">📐 Dopasowanie i Trening (4)</button>
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

# 11. Strona główna mojniezbednik.pl (4 główne działy + wyszukiwarka wszystkich 114 narzędzi)
all_cards = listy_cards + kuchnia_cards + warsztat_cards + rower_cards

HOME_BODY = f"""
<h1 data-i18n="home_h1">⚡ MójNiezbędnik.pl – Praktyczne parametry, tabele i interaktywne listy</h1>
<p data-i18n="home_sub">Szybkie punkty wyjścia z podanymi warunkami oraz interaktywne checklisty do druku – bez zbędnych wstępów. Wybierz dział lub wyszukaj narzędzie poniżej:</p>
<div class="grid" style="margin-bottom:2rem;">
    <a href="/listy/" class="card" style="border-color:var(--accent);">
        <span class="badge" data-i18n="cat_lists_b">12 interaktywnych list</span>
        <h3 data-i18n="cat_lists_h">🎒 Listy i Niezbędniki</h3>
        <p class="card-val" data-i18n="cat_lists_p">Co zabrać na obóz, kolonie, zimowisko, biwak, bikepacking i do szpitala (Druk A4 / PDF)</p>
    </a>
    <a href="/kuchnia/" class="card" style="border-color:var(--accent);">
        <span class="badge" data-i18n="cat_kitch_b">38 pozycji</span>
        <h3 data-i18n="cat_kitch_h">🍳 Kuchnia & Airfryer</h3>
        <p class="card-val" data-i18n="cat_kitch_p">Orientacyjne czasy, kryteria temperatury (74°C dla drobiu) + minutnik z Wake Lock</p>
    </a>
    <a href="/warsztat/" class="card" style="border-color:var(--accent);">
        <span class="badge" data-i18n="cat_work_b">38 pozycji + Kalkulatory</span>
        <h3 data-i18n="cat_work_h">🔧 Warsztat, Remont & DIY</h3>
        <p class="card-val" data-i18n="cat_work_p">Kalkulator farby i betonu, wiertła pod gwinty M2–M20, obróbka cieplna stali, druk 3D</p>
    </a>
    <a href="/rower/" class="card" style="border-color:var(--accent);">
        <span class="badge" data-i18n="cat_bike_b">26 pozycji + Kalkulator</span>
        <h3 data-i18n="cat_bike_h">🚲 Rower & Serwis</h3>
        <p class="card-val" data-i18n="cat_bike_p">Kalkulator ciśnienia (Hooked / Hookless), dawki mleczka tubeless, momenty Nm</p>
    </a>
</div>

<h2 data-i18n="home_search_h">🔍 Wyszukiwarka wszystkich 114 narzędzi, kalkulatorów i list</h2>
<label for="q" data-i18n="home_search_lbl">Wpisz szukaną frazę (obsługuje zapytania bez polskich znaków i spacji, np. farba, beton, oboz, piers, m 8, 40-622):</label>
<input type="text" id="q" placeholder="Szukaj np. farba, beton, obóz, kurczak, M8, 1.2842, PETG, 40c..." oninput="filterHome()">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:0.5rem;">
    <span id="viewStatus" style="font-size:0.9rem; color:var(--muted);">Wyświetlono: 20 wybranych narzędzi i list</span>
    <button class="btn-secondary" id="toggleAllBtn" onclick="showAllTools()" style="padding:0.45rem 0.9rem; font-size:0.85rem;">Pokaż wszystkie 114 pozycji</button>
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
            statusEl.textContent = isEn ? "Showing full catalog: all 114 tools & lists" : "Wyświetlono pełny katalog: wszystkie 114 narzędzi i list";
            btnEl.textContent = isEn ? "Collapse to 20 featured" : "Zwiń do 20 wybranych";
        }} else {{
            statusEl.textContent = isEn ? "Showing: 20 featured tools across 4 categories" : "Wyświetlono: 20 wybranych pozycji z 4 działów";
            btnEl.textContent = isEn ? "Show all 114 items" : "Pokaż wszystkie 114 pozycji";
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

# 12. Generowanie sitemap.xml (119 adresów URL) oraz robots.txt
sitemap_entries = "\n".join([f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in all_urls])
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

print(f"✅ GOTOWE! Wygenerowano łącznie {len(all_urls)} adresów URL w {BASE_DIR}")
