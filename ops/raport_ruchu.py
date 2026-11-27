#!/usr/bin/env python3
"""Statystyki ruchu z logów nginx (bez ciasteczek i bez zewnętrznych usług).

Uruchamiany z crona roota co 15 minut:
    */15 * * * * /usr/bin/python3 /usr/local/sbin/raport_ruchu.py >/dev/null 2>&1
    55 23 * * * /usr/bin/python3 /usr/local/sbin/raport_ruchu.py --whatsapp >/dev/null 2>&1

Jak liczy:
- mojniezbednik.pl: każda strona wysyła w tle zapytanie /hit?p=<strona>&r=<domena źródła>.
  Wysyłają je tylko przeglądarki, które wykonują JavaScript, więc większość botów odpada.
  Dni sprzed wdrożenia licznika (bez żadnych /hit) liczone są starą metodą (User-Agent).
- park-swiatowida.pl: stara metoda (User-Agent), bo ta strona nie ma licznika.
- Twoje wejścia są pomijane: na telefonie raz otwórz https://mojniezbednik.pl/?ja=1
  (?ja=0 cofa). Dodatkowo pomijane są adresy IP, które danego dnia otworzyły stronę statystyk.
- Historia dzienna (same liczby, bez adresów IP) trafia do HISTORIA_JSON, więc statystyki
  sięgają dalej niż logi nginx (które są kasowane po ok. 14 dniach).
"""
import glob
import gzip
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from html import escape
from zoneinfo import ZoneInfo

# --- 1. KONFIGURACJA ---
STRONY = {
    "Mój Niezbędnik": "/var/log/nginx/access.log",
    "Park Światowida": "/var/log/nginx/swiatowida_access.log",
}
ANONIMOWE = {"Park Światowida"}           # log bez prawdziwych adresów IP
WLASNE_DOMENY = ("mojniezbednik.pl", "park-swiatowida.pl")
SCIEZKA_HTML = "/var/www/hub/statystyki-tajne-987.html"
HISTORIA_JSON = "/var/lib/raport-ruchu/historia.json"
STREFA = ZoneInfo("Europe/Warsaw")
DNI_HISTORII = 400

# WhatsApp przez CallMeBot (opcjonalnie). Można też ustawić w /etc/raport-ruchu.env:
#   WHATSAPP_TELEFON=+48...   WHATSAPP_APIKEY=...
WHATSAPP_TELEFON = ""
WHATSAPP_APIKEY = ""

# --- 2. FILTRY ---
BOT_REGEX = re.compile(
    r"bot|crawl|slurp|spider|mediapartners|ahrefs|semrush|mj12|dotbot|petalbot|bytespider|"
    r"gptbot|claude|anthropic|perplexity|bingpreview|facebookexternalhit|meta-external|"
    r"python|requests|aiohttp|httpx|go-http|java/|okhttp|node-fetch|axios|curl|wget|"
    r"headless|phantom|selenium|playwright|puppeteer|lighthouse|pagespeed|uptime|statuscake|"
    r"pingdom|monitor|yandex|baidu|duckduckbot|sogou|exabot|ia_archiver|scan|zgrab|masscan|"
    r"nmap|nikto|censys|shodan|expanse|leakix|netcraft|preview|fetch|feed|wordpress|"
    r"^mozilla/5\.0$",
    re.IGNORECASE,
)
STATIC_EXT_REGEX = re.compile(
    r"\.(css|js|jpg|jpeg|png|gif|ico|svg|woff2?|ttf|eot|mp4|webp|map|txt|xml|json|webmanifest)(\?.*)?$",
    re.IGNORECASE,
)
SKANY_REGEX = re.compile(r"\.(php|asp|aspx|env|git|sql|bak|cgi)|wp-|/\.", re.IGNORECASE)
LOG_REGEX = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<date>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) [^"]*" '
    r'(?P<status>\d+) \S+ "(?P<ref>[^"]*)" "(?P<ua>[^"]*)"'
)

ZRODLA = [
    ("google.", "Google"), ("bing.", "Bing"), ("duckduckgo.", "DuckDuckGo"),
    ("yahoo.", "Yahoo"), ("ecosia.", "Ecosia"), ("wykop.", "Wykop"),
    ("pinterest.", "Pinterest"), ("pin.it", "Pinterest"), ("reddit.", "Reddit"),
    ("facebook.", "Facebook"), ("fb.", "Facebook"), ("instagram.", "Instagram"),
    ("youtube.", "YouTube"), ("t.co", "X / Twitter"), ("x.com", "X / Twitter"),
    ("chatgpt.", "ChatGPT"), ("openai.", "ChatGPT"), ("perplexity.", "Perplexity"),
    ("claude.ai", "Claude"), ("gemini.", "Gemini"), ("copilot.", "Copilot"),
]


def nazwa_zrodla(host):
    host = (host or "").lower().strip()
    if host.startswith("www."):
        host = host[4:]
    if not host or host == "-":
        return "Bezpośrednio / aplikacje"
    if any(host == d or host.endswith("." + d) for d in WLASNE_DOMENY):
        return None  # przejście wewnątrz strony
    for wzor, nazwa in ZRODLA:
        if wzor in host:
            return nazwa
    return host


def host_z_url(url):
    try:
        return urllib.parse.urlsplit(url).hostname or ""
    except ValueError:
        return ""


def normuj_strone(path):
    path = urllib.parse.unquote(path.split("?", 1)[0].split("#", 1)[0])
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    return path or "/"


def parsuj_date(txt):
    try:
        return datetime.strptime(txt, "%d/%b/%Y:%H:%M:%S %z").astimezone(STREFA)
    except ValueError:
        return None


def nowy_dzien():
    return {"ludzie": 0, "ip": set(), "calosc": 0, "boty": 0,
            "zrodla": Counter(), "strony": Counter(), "en": 0, "metoda": "ua"}


# --- 3. ANALIZA LOGÓW ---
def czytaj_linie(baza):
    for sciezka in sorted(glob.glob(baza + "*")):
        try:
            otworz = gzip.open if sciezka.endswith(".gz") else open
            with otworz(sciezka, "rt", encoding="utf-8", errors="ignore") as plik:
                for linia in plik:
                    m = LOG_REGEX.match(linia)
                    if m:
                        yield m
        except OSError:
            continue


def analizuj(baza, start_licznika=None):
    """Zwraca (dni, najstarszy_wpis). dni: data -> statystyki dnia.
    start_licznika: pierwszy dzień z /hit zapisany w historii (od niego zawsze metoda licznika)."""
    wpisy = []
    moje_ip = defaultdict(set)    # dzień -> IP, które oglądały statystyki
    z_licznikiem = set()          # dni, w których działał /hit
    najstarszy = None

    for m in czytaj_linie(baza):
        dt = parsuj_date(m.group("date"))
        if not dt:
            continue
        if najstarszy is None or dt < najstarszy:
            najstarszy = dt
        dzien = dt.strftime("%Y-%m-%d")
        path, ip = m.group("path"), m.group("ip")
        if "statystyki-tajne" in path:
            moje_ip[dzien].add(ip)
            continue
        if path.startswith("/hit?"):
            z_licznikiem.add(dzien)
        wpisy.append((dzien, ip, m.group("method"), path, int(m.group("status")),
                      m.group("ref"), m.group("ua")))

    if z_licznikiem:
        pierwszy = min(z_licznikiem)
        start_licznika = min(start_licznika, pierwszy) if start_licznika else pierwszy
    # od wdrożenia licznika liczymy nim także dni bez żadnego /hit (wtedy ludzi = 0)
    if start_licznika:
        z_licznikiem |= {w[0] for w in wpisy if w[0] >= start_licznika}

    dni = defaultdict(nowy_dzien)
    for dzien, ip, metoda, path, status, ref, ua in wpisy:
        if ip in moje_ip[dzien]:
            continue
        d = dni[dzien]
        bot_ua = bool(BOT_REGEX.search(ua)) or ua in ("-", "")

        if path.startswith("/hit?"):
            if dzien not in z_licznikiem or bot_ua:
                continue
            q = urllib.parse.parse_qs(path.split("?", 1)[1])
            strona = normuj_strone(q.get("p", ["/"])[0])
            d["metoda"] = "licznik"
            d["ludzie"] += 1
            d["ip"].add(ip)
            d["strony"][strona] += 1
            if strona.startswith("/en/") or strona == "/en":
                d["en"] += 1
            zrodlo = nazwa_zrodla(q.get("r", [""])[0])
            if zrodlo:
                d["zrodla"][zrodlo] += 1
            continue

        # zwykłe odsłony stron (HTML)
        if status >= 400 or metoda not in ("GET", "HEAD") or STATIC_EXT_REGEX.search(path) \
                or SKANY_REGEX.search(path) or path == "/hit":
            continue
        d["calosc"] += 1
        if dzien in z_licznikiem:
            continue  # ludzi liczy już /hit
        if bot_ua or metoda == "HEAD":
            d["boty"] += 1
            continue
        strona = normuj_strone(path)
        d["ludzie"] += 1
        if ip != "0.0.0.0":
            d["ip"].add(ip)
        d["strony"][strona] += 1
        if strona.startswith("/en/") or strona == "/en":
            d["en"] += 1
        zrodlo = nazwa_zrodla(host_z_url(ref))
        if zrodlo:
            d["zrodla"][zrodlo] += 1

    for dzien in z_licznikiem:
        d = dni[dzien]
        d["metoda"] = "licznik"
        d["boty"] = max(d["calosc"] - d["ludzie"], 0)
    return dni, najstarszy


# --- 4. HISTORIA (same liczby, bez IP) ---
def wczytaj_historie():
    try:
        with open(HISTORIA_JSON, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def zapisz_historie(hist):
    os.makedirs(os.path.dirname(HISTORIA_JSON), exist_ok=True)
    tmp = HISTORIA_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, HISTORIA_JSON)


def do_json(d):
    return {"ludzie": d["ludzie"], "odw": len(d["ip"]), "calosc": d["calosc"],
            "boty": d["boty"], "en": d["en"], "metoda": d["metoda"],
            "zrodla": dict(d["zrodla"].most_common(30)),
            "strony": dict(d["strony"].most_common(60))}


def aktualizuj_historie(hist, nazwa, dni, najstarszy):
    stara = hist.get(nazwa, {})
    pierwszy_pelny = najstarszy.strftime("%Y-%m-%d") if najstarszy else None
    for dzien, d in dni.items():
        nowe = do_json(d)
        # najstarszy dzień w logach bywa niepełny - nie nadpisuj lepszych danych
        if dzien == pierwszy_pelny and dzien in stara and stara[dzien]["calosc"] > nowe["calosc"]:
            continue
        stara[dzien] = nowe
    granica = (datetime.now(STREFA) - timedelta(days=DNI_HISTORII)).strftime("%Y-%m-%d")
    hist[nazwa] = {k: v for k, v in stara.items() if k >= granica}


# --- 5. RAPORT HTML ---
OKRESY = [("dzisiaj", "Dzisiaj", 1), ("7d", "7 dni", 7), ("30d", "30 dni", 30),
          ("90d", "90 dni", 90), ("365d", "Rok", 365)]


def sumuj(dni_strony, ile_dni):
    dzis = datetime.now(STREFA).replace(hour=0, minute=0, second=0, microsecond=0)
    od = (dzis - timedelta(days=ile_dni - 1)).strftime("%Y-%m-%d")
    s = {"ludzie": 0, "odw": 0, "calosc": 0, "boty": 0, "en": 0,
         "zrodla": Counter(), "strony": Counter(), "dni": 0}
    for dzien, d in dni_strony.items():
        if dzien < od:
            continue
        s["dni"] += 1
        for k in ("ludzie", "odw", "calosc", "boty", "en"):
            s[k] += d.get(k, 0)
        s["zrodla"].update(d.get("zrodla", {}))
        s["strony"].update(d.get("strony", {}))
    return s


def tabela_top(licznik, naglowek, n=10, linki=False):
    if not licznik:
        return f'<p class="muted">{naglowek}: brak danych.</p>'
    razem = sum(licznik.values()) or 1
    wiersze = ""
    for nazwa, ile in licznik.most_common(n):
        pct = round(ile * 100 / razem)
        tekst = escape(nazwa)
        if linki and nazwa.startswith("/"):
            tekst = f'<a href="{escape(nazwa)}" target="_blank" rel="noopener">{tekst}</a>'
        wiersze += (f'<tr><td class="name">{tekst}</td><td class="num">{ile}</td>'
                    f'<td class="barcell"><div class="mini" style="width:{pct}%"></div></td></tr>')
    return (f'<h3>{naglowek}</h3><div class="table-wrap"><table class="top">'
            f"<tbody>{wiersze}</tbody></table></div>")


def karta(nazwa, s, anonim):
    procent = round(s["ludzie"] * 100 / s["calosc"], 1) if s["calosc"] else 0
    odw = "brak IP w logu" if anonim else f'{s["odw"]} dziennych odwiedzających'
    en = ""
    if s["en"]:
        en = f'<span class="sub">w tym wersja EN: {s["en"]} ({round(s["en"] * 100 / max(s["ludzie"], 1))}%)</span>'
    return f"""
    <div class="card">
      <h2>{escape(nazwa)}</h2>
      <div class="grid">
        <div class="stat-box human"><span class="label">Ludzie</span>
          <span class="val">{s["ludzie"]} <small>odsłon</small></span>
          <span class="sub">{odw}</span>{en}</div>
        <div class="stat-box total"><span class="label">Wszystkie zapytania o strony</span>
          <span class="val">{s["calosc"]}</span>
          <span class="sub">ludzie to {procent}%</span></div>
        <div class="stat-box bot"><span class="label">Boty i automaty</span>
          <span class="val">{s["boty"]}</span>
          <span class="sub">dni z danymi: {s["dni"]}</span></div>
      </div>
      <div class="two">
        <div>{tabela_top(s["zrodla"], "Skąd przychodzą")}</div>
        <div>{tabela_top(s["strony"], "Najczęściej czytane", linki=not anonim)}</div>
      </div>
    </div>"""


def generuj_html(hist, czas):
    zakladki, sekcje = "", ""
    for i, (kod, tytul, ile) in enumerate(OKRESY):
        aktywny = " active" if i == 0 else ""
        zakladki += f'<button class="tab-btn{aktywny}" data-target="tab-{kod}">{tytul}</button>'
        karty = ""
        for nazwa in STRONY:
            dni = hist.get(nazwa)
            if not dni:
                karty += f'<div class="card"><h2>{escape(nazwa)}</h2><p>Brak danych</p></div>'
                continue
            karty += karta(nazwa, sumuj(dni, ile), nazwa in ANONIMOWE)
        sekcje += f'<div id="tab-{kod}" class="tab-content{aktywny}">{karty}</div>'

    tabele = ""
    for nazwa in STRONY:
        dni = hist.get(nazwa, {})
        if not dni:
            continue
        wiersze = ""
        for dzien in sorted(dni, reverse=True)[:30]:
            d = dni[dzien]
            top = max(d.get("zrodla", {}).items(), key=lambda kv: kv[1], default=("", 0))[0]
            znak = "" if d.get("metoda") == "licznik" else ' <small title="liczone po User-Agent">*</small>'
            wiersze += (f'<tr><td>{dzien}{znak}</td><td class="c-green"><b>{d["ludzie"]}</b></td>'
                        f'<td>{"-" if nazwa in ANONIMOWE else d["odw"]}</td>'
                        f'<td class="c-blue">{d["calosc"]}</td><td class="c-red">{d["boty"]}</td>'
                        f"<td>{escape(top)}</td></tr>")
        tabele += f"""
    <div class="card"><h2>Dzień po dniu (30 dni): {escape(nazwa)}</h2>
      <div class="table-wrap"><table><thead><tr><th>Data</th><th>Ludzie</th><th>Odwiedzający</th>
      <th>Całość</th><th>Boty</th><th>Główne źródło</th></tr></thead><tbody>{wiersze}</tbody></table></div>
      <p class="muted">* dzień liczony starą metodą (po User-Agent), mniej dokładnie.</p></div>"""

    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="300">
<title>Statystyki ruchu</title>
<style>
body {{ font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 16px; }}
.container {{ max-width: 960px; margin: 0 auto; }}
header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }}
h1 {{ margin: 0; font-size: 1.4rem; }} h3 {{ font-size: 1rem; color: #cbd5e1; margin: 12px 0 6px; }}
.time, .muted {{ color: #94a3b8; font-size: 0.85rem; }}
.tabs {{ display: flex; gap: 6px; margin-bottom: 16px; flex-wrap: wrap; }}
.tab-btn {{ background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 10px 14px; border-radius: 8px; cursor: pointer; font-weight: 600; min-height: 44px; }}
.tab-btn.active {{ background: #3b82f6; color: #fff; border-color: #3b82f6; }}
.tab-content {{ display: none; }} .tab-content.active {{ display: block; }}
.card {{ background: #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 16px; border: 1px solid #334155; }}
.card h2 {{ margin-top: 0; font-size: 1.15rem; color: #38bdf8; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }}
.two {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
.stat-box {{ background: #0f172a; padding: 14px; border-radius: 8px; display: flex; flex-direction: column; border-left: 4px solid #64748b; }}
.stat-box.human {{ border-left-color: #22c55e; }} .stat-box.total {{ border-left-color: #3b82f6; }} .stat-box.bot {{ border-left-color: #ef4444; }}
.label {{ font-size: 0.85rem; color: #94a3b8; }} .val {{ font-size: 1.6rem; font-weight: bold; }}
.val small {{ font-size: 0.85rem; font-weight: normal; color: #94a3b8; }} .sub {{ font-size: 0.85rem; color: #cbd5e1; margin-top: 2px; }}
.table-wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #334155; }}
th {{ color: #94a3b8; background: #0f172a; }} td:first-child {{ white-space: nowrap; }}
table.top td {{ padding: 6px 8px; }} td.name {{ word-break: break-all; }} td.num {{ text-align: right; font-weight: 600; width: 3.5em; }}
td.barcell {{ width: 30%; }} .mini {{ height: 8px; background: #22c55e; border-radius: 4px; min-width: 2px; }}
a {{ color: #93c5fd; }}
.c-green {{ color: #4ade80; }} .c-blue {{ color: #60a5fa; }} .c-red {{ color: #f87171; }}
</style>
</head>
<body>
<div class="container">
<header><h1>Ruch na stronach</h1><span class="time">Aktualizacja: {czas}</span></header>
<div class="tabs">{zakladki}</div>
{sekcje}
{tabele}
<p class="muted">Własne wejścia: otwórz raz na swoim telefonie i komputerze https://mojniezbednik.pl/?ja=1 (cofnięcie: ?ja=0).</p>
</div>
<script>
document.querySelectorAll('.tab-btn').forEach(function (btn) {{
  btn.addEventListener('click', function () {{
    document.querySelectorAll('.tab-btn').forEach(function (b) {{ b.classList.remove('active'); }});
    document.querySelectorAll('.tab-content').forEach(function (c) {{ c.classList.remove('active'); }});
    btn.classList.add('active');
    document.getElementById(btn.getAttribute('data-target')).classList.add('active');
  }});
}});
</script>
</body>
</html>"""


# --- 6. WHATSAPP ---
def konfiguracja_whatsapp():
    tel, klucz = WHATSAPP_TELEFON, WHATSAPP_APIKEY
    try:
        with open("/etc/raport-ruchu.env", encoding="utf-8") as f:
            for linia in f:
                k, _, v = linia.strip().partition("=")
                if k == "WHATSAPP_TELEFON":
                    tel = v.strip().strip('"')
                elif k == "WHATSAPP_APIKEY":
                    klucz = v.strip().strip('"')
    except OSError:
        pass
    return tel, klucz


def wyslij_whatsapp(tekst):
    tel, klucz = konfiguracja_whatsapp()
    if not tel or not klucz:
        print("WhatsApp nieskonfigurowany - pomijam.")
        return
    url = ("https://api.callmebot.com/whatsapp.php?phone=" + urllib.parse.quote(tel.replace(" ", ""))
           + "&text=" + urllib.parse.quote(tekst) + "&apikey=" + urllib.parse.quote(klucz))
    try:
        urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15)
    except Exception as e:  # noqa: BLE001
        print(f"Błąd wysyłania na WhatsApp: {e}")


# --- 7. START ---
def main():
    hist = wczytaj_historie()
    for nazwa, sciezka in STRONY.items():
        start = min((k for k, v in hist.get(nazwa, {}).items() if v.get("metoda") == "licznik"), default=None)
        dni, najstarszy = analizuj(sciezka, start)
        if dni:
            aktualizuj_historie(hist, nazwa, dni, najstarszy)
    zapisz_historie(hist)

    czas = datetime.now(STREFA).strftime("%Y-%m-%d %H:%M")
    tmp = SCIEZKA_HTML + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(generuj_html(hist, czas))
    os.chmod(tmp, 0o644)
    os.replace(tmp, SCIEZKA_HTML)
    print(f"Zaktualizowano: {SCIEZKA_HTML}")

    if "--whatsapp" in sys.argv:
        linie = [f"📊 Raport stron ({datetime.now(STREFA).strftime('%d.%m')})"]
        for nazwa in STRONY:
            dni = hist.get(nazwa)
            if not dni:
                continue
            dzis, tydz = sumuj(dni, 1), sumuj(dni, 7)
            top = tydz["zrodla"].most_common(1)
            linie.append(f"{nazwa}\n• Dziś: {dzis['ludzie']} odsłon ludzi (boty: {dzis['boty']})\n"
                         f"• 7 dni: {tydz['ludzie']}" + (f", najwięcej z: {top[0][0]}" if top else ""))
        wyslij_whatsapp("\n\n".join(linie))


if __name__ == "__main__":
    main()
