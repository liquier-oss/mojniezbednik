# mojniezbednik.pl – automatyzacja

```
update_hub.py                ← generator strony (zapisuje do /var/www/hub)
ops/                         ← skrypty serwera
.github/workflows/deploy.yml ← automatyczne wdrożenie
```

Zasada: **Claude proponuje (PR) → Ty zatwierdzasz → GitHub sam wdraża.**
Od teraz zmieniaj `update_hub.py` tylko przez GitHub, nie na serwerze.

Jak działa wdrożenie: GitHub sprawdza składnię → łączy się z VPS kluczem, który
może uruchomić **tylko** `/usr/local/sbin/mojniezbednik-deploy` → serwer robi
`git pull`, kopię strony i `python3 update_hub.py` (przy błędzie przywraca kopię) →
czyszczenie cache Cloudflare.

---

## Krok 1. Pobierz te pliki na serwer

```bash
cd ~/mojniezbednik && git pull
```

## Krok 2. Snapshot VPS w panelu OVH

Zrób go przed krokiem 3. Zostaw otwartą drugą sesję SSH, dopóki nie sprawdzisz, że logowanie działa.

## Krok 3. Zabezpieczenie serwera i użytkownik deploy

```bash
ssh-keygen -t ed25519 -N "" -C "github-actions" -f ~/deploy_key
cd ~/mojniezbednik
sudo bash ops/setup-server.sh ~/deploy_key.pub
```
Robi: automatyczne łatki, fail2ban, SSH tylko na klucz (jeśli masz klucz),
firewall – www tylko z Cloudflare, użytkownika `deploy`, cron.

Na końcu wypisze klucz zaczynający się od `ssh-ed25519 ... vps-read-only`.
Dodaj go: GitHub → repo → Settings → **Deploy keys** → Add (bez „Allow write access”).

Potem pobierz repo dla użytkownika deploy i sprawdź wdrożenie ręcznie:
```bash
sudo -u deploy git clone git@github.com:liquier-oss/mojniezbednik.git /home/deploy/mojniezbednik
sudo -u deploy /usr/local/sbin/mojniezbednik-deploy
```
Powinno skończyć się `OK: strona wygenerowana`.

## Krok 4. Sekrety w GitHubie

Repo → Settings → Secrets and variables → Actions → New repository secret:

| Nazwa | Skąd wziąć |
|---|---|
| `VPS_HOST` | IP serwera z panelu OVH |
| `VPS_KNOWN_HOSTS` | wynik `ssh-keyscan -t ed25519 <IP_VPS>` |
| `DEPLOY_SSH_KEY` | `cat ~/deploy_key` (całość) |
| `CF_ZONE_ID` | Cloudflare → domena → Overview → Zone ID |
| `CF_API_TOKEN` | Cloudflare → My Profile → API Tokens → Create → Custom: *Zone / Cache Purge / Purge*, tylko ta domena |

Następnie: `rm ~/deploy_key` i test: GitHub → Actions → Deploy → **Run workflow**.

## Krok 5. Nagłówki nginx

```bash
sudo nano /etc/nginx/sites-enabled/mojniezbednik
```
W bloku `server { ... }` z `listen 443` dopisz:
```
include snippets/security-headers.conf;
```
i usuń stare linie `add_header` dla tych samych nagłówków. Potem:
```bash
sudo nginx -t && sudo systemctl reload nginx
```
Sprawdź wynik na securityheaders.com.

## Krok 6. Codzienny audyt z Claude

```bash
sudo npm install -g @anthropic-ai/claude-code   # jeśli brak npm: sudo apt install -y nodejs npm
sudo nano /etc/audyt.env
```
Zawartość `/etc/audyt.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
NTFY_TOPIC=mojniezbednik-xxxxxxxxxxxx
WEB_ROOT=/var/www/hub
DOMAIN=mojniezbednik.pl
```
```bash
sudo chmod 600 /etc/audyt.env
sudo /usr/local/sbin/audyt.sh && sudo ls /var/log/audyt/   # test
```
Powiadomienia: aplikacja **ntfy** na telefonie, subskrypcja tego samego `NTFY_TOPIC`
(długa, losowa nazwa – działa jak hasło). Claude dostaje tylko zebrany tekst, bez dostępu do serwera.

## Krok 7. Zmiany na stronie z telefonu

Aplikacja Claude → **Code** → repo `liquier-oss/mojniezbednik` → napisz, co zmienić.
Claude robi PR → przeglądasz → **Merge** → po ~1 min zmiana jest na stronie.

Pierwsze zadanie warte zlecenia:
> W update_hub.py przenieś skrypty inline do osobnych plików .js, żeby można było usunąć 'unsafe-inline' z CSP.

Po wdrożeniu przełącz CSP na „KROK 2” w `/etc/nginx/snippets/security-headers.conf`.
