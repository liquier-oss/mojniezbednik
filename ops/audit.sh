#!/usr/bin/env bash
# Codzienny audyt serwera mojniezbednik.pl
# 1) Skrypt sam zbiera dane (Claude NIE dostaje dostępu do serwera).
# 2) Claude tylko czyta zebrany tekst i pisze raport po polsku.
# 3) Raport trafia do /var/log/audyt/ i (opcjonalnie) jako powiadomienie na telefon (ntfy).
#
# Wymaga: Claude Code (npm install -g @anthropic-ai/claude-code)
# oraz pliku /etc/audyt.env z treścią:
#   ANTHROPIC_API_KEY=sk-ant-...
#   NTFY_TOPIC=dluga-losowa-nazwa      (opcjonalnie; aplikacja "ntfy" na telefon)
#   WEB_ROOT=/var/www/hub
#   DOMAIN=mojniezbednik.pl
set -uo pipefail

set -a; . /etc/audyt.env; set +a
: "${WEB_ROOT:=/var/www/hub}"
: "${DOMAIN:=mojniezbednik.pl}"

OUT_DIR=/var/log/audyt
mkdir -p "$OUT_DIR"
DATA=$(mktemp)
TODAY=$(date +%F)

section() { printf '\n===== %s =====\n' "$1"; }

{
  section "System";            lsb_release -ds 2>/dev/null; uname -r; uptime
  section "Aktualizacje do zainstalowania"; apt list --upgradable 2>/dev/null | tail -n +2
  section "Wymagany restart";  if [ -f /var/run/reboot-required ]; then cat /var/run/reboot-required.pkgs 2>/dev/null; else echo "nie"; fi
  section "Dysk";              df -h / "$WEB_ROOT"
  section "Pamięć";            free -h
  section "Usługi";            for s in nginx ssh fail2ban unattended-upgrades; do printf '%s: %s\n' "$s" "$(systemctl is-active $s)"; done
  section "fail2ban sshd";     fail2ban-client status sshd 2>&1 | tail -n 6
  section "SSH - aktywne ustawienia"; sshd -T 2>/dev/null | grep -iE "^(passwordauthentication|permitrootlogin|allowusers|maxauthtries) "
  section "SSH - udane logowania (24h)"; journalctl -u ssh --since "24 hours ago" --no-pager 2>/dev/null | grep -i "accepted" | tail -n 20
  section "SSH - nieudane próby (24h, liczba)"; journalctl -u ssh --since "24 hours ago" --no-pager 2>/dev/null | grep -Eic "failed|invalid user"
  section "Firewall";          ufw status | head -n 8; echo "(reguł cloudflare: $(ufw status | grep -c cloudflare))"
  section "Otwarte porty";     ss -tulpn | grep LISTEN
  section "Certyfikat na serwerze (origin)"
  echo | openssl s_client -connect 127.0.0.1:443 -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -subject -issuer -enddate 2>/dev/null || echo "brak/nie udało się odczytać"
  section "Certyfikaty Let's Encrypt (certbot)"
  if command -v certbot >/dev/null; then certbot certificates 2>/dev/null | grep -E "Certificate Name|Domains|Expiry"; echo "Timer odnawiania: $(systemctl is-active certbot.timer 2>/dev/null)"; else echo "brak certbot"; fi
  section "nginx - ostatnie błędy"; tail -n 40 /var/log/nginx/error.log 2>/dev/null
  section "nginx - najczęstsze odpowiedzi 4xx/5xx"
  awk '$9 ~ /^[45][0-9][0-9]$/ {print $9, $7}' /var/log/nginx/access.log 2>/dev/null | sort | uniq -c | sort -rn | head -n 20
  section "nginx - najaktywniejsze IP"
  awk '{print $1}' /var/log/nginx/access.log 2>/dev/null | sort | uniq -c | sort -rn | head -n 10
  section "Pliki strony zmienione w ostatniej dobie"; find "$WEB_ROOT" -type f -mtime -1 2>/dev/null | head -n 50
  section "Pliki strony z niebezpiecznymi uprawnieniami (zapis dla wszystkich)"; find "$WEB_ROOT" -perm -o+w 2>/dev/null | head -n 20
  section "Pliki wykonywalne/skrypty serwerowe w katalogu strony (nie powinno ich być)"
  find "$WEB_ROOT" -type f \( -name '*.php' -o -name '*.sh' -o -name '*.py' -o -name '*.cgi' \) 2>/dev/null | head -n 20
} > "$DATA" 2>&1

PROMPT="Jesteś administratorem bezpieczeństwa. Poniżej dane z serwera VPS (Ubuntu, nginx; dwie strony: ${DOMAIN} za Cloudflare oraz park-swiatowida.pl bezpośrednio z certyfikatem Let's Encrypt; porty 80/443 celowo otwarte dla wszystkich). Napisz krótki raport po polsku (max 15 linii): na początku jedna linia STATUS: OK / UWAGA / ALARM, potem konkretne problemy od najważniejszego i dokładne polecenia naprawy. Nie wymyślaj problemów, których nie ma w danych. Strona jest generowana skryptem update_hub.py (z GitHuba) do /var/www/hub - zmienione tam pliki .html są normalne po wdrożeniu; podejrzane są pliki .php/.sh/.py lub nieznane katalogi. Na serwerze działa też cron root z /root/raport_ruchu.py - to znany, własny skrypt. Logowanie hasłem SSH dla użytkownika ubuntu jest świadomym wyborem właściciela (chronione fail2ban) - nie zgłaszaj go jako problemu, zgłaszaj tylko podejrzane udane logowania z nieznanych IP. Użytkownik deploy logujący się kluczem z adresów Azure/Microsoft to GitHub Actions (wdrożenia) - klucz ma wymuszoną komendę, to normalne. Ostrzegaj, jeśli certyfikat Let's Encrypt wygasa za mniej niż 20 dni albo timer certbot nie jest aktywny. Plik statystyki-tajne-987.html jest chroniony hasłem (auth_basic) - to celowe."

cd "$(mktemp -d)"
REPORT=$(claude -p "$PROMPT" --model sonnet \
          --disallowedTools "Bash,Edit,Write,NotebookEdit,WebFetch,WebSearch" < "$DATA" 2>&1) \
  || REPORT="STATUS: ALARM - audyt nie zadziałał (błąd Claude Code): $REPORT"

printf '%s\n\n--- DANE ---\n' "$REPORT" > "$OUT_DIR/$TODAY.txt"
cat "$DATA" >> "$OUT_DIR/$TODAY.txt"
rm -f "$DATA"

# Zostaw raporty z ostatnich 60 dni
find "$OUT_DIR" -name '*.txt' -mtime +60 -delete

if [ -n "${NTFY_TOPIC:-}" ]; then
  PRIO=default
  echo "$REPORT" | head -n1 | grep -q "ALARM" && PRIO=urgent
  echo "$REPORT" | head -n1 | grep -q "UWAGA" && PRIO=high
  curl -fsS -H "Title: Audyt ${DOMAIN} ${TODAY}" -H "Priority: ${PRIO}" \
       -d "$REPORT" "https://ntfy.sh/${NTFY_TOPIC}" >/dev/null || true
fi
