#!/usr/bin/env bash
# Wpuszcza ruch na porty 80/443 tylko z adresów Cloudflare i ustawia w nginx
# prawdziwe IP odwiedzających (zamiast IP Cloudflare) w logach.
# Uruchamiaj jako root. Bezpieczne do ponownego uruchamiania (cron co tydzień).
set -euo pipefail

V4=$(curl -fsS --max-time 20 https://www.cloudflare.com/ips-v4)
V6=$(curl -fsS --max-time 20 https://www.cloudflare.com/ips-v6)

# Nie ruszaj niczego, jeśli lista się nie pobrała (inaczej strona by padła).
if [ "$(echo "$V4" | grep -c '/')" -lt 5 ]; then
  echo "Nie udało się pobrać listy IP Cloudflare - przerywam bez zmian." >&2
  exit 1
fi

# 1) Usuń stare reguły oznaczone komentarzem "cloudflare" (od końca, żeby numery się nie przesuwały)
for n in $(ufw status numbered | grep '# cloudflare' | sed -E 's/^\[ *([0-9]+)\].*/\1/' | sort -rn); do
  ufw --force delete "$n" >/dev/null
done

# 2) Dodaj aktualne
for ip in $V4 $V6; do
  ufw allow proto tcp from "$ip" to any port 80,443 comment cloudflare >/dev/null
done

# 3) Prawdziwe IP odwiedzających w nginx
CONF=/etc/nginx/conf.d/cloudflare-realip.conf
# Jeśli inny plik już ustawia real_ip_header, nie dubluj (nginx by się nie uruchomił)
if grep -rlq "real_ip_header" /etc/nginx --exclude="$(basename "$CONF")" 2>/dev/null; then
  rm -f "$CONF"
  echo "OK: reguły firewall Cloudflare zaktualizowane; real_ip ustawia już inny plik nginx - pomijam."
  exit 0
fi
{
  echo "# Generowane automatycznie przez cloudflare-only.sh - nie edytuj ręcznie"
  for ip in $V4 $V6; do echo "set_real_ip_from $ip;"; done
  echo "real_ip_header CF-Connecting-IP;"
} > "$CONF.new"
mv "$CONF.new" "$CONF"

if nginx -t 2>/dev/null; then
  systemctl reload nginx
else
  rm -f "$CONF"
  echo "Uwaga: nginx -t zgłaszał błąd - usunięto $CONF, nginx bez zmian." >&2
  nginx -t || true
fi

echo "OK: reguły Cloudflare zaktualizowane ($(echo $V4 $V6 | wc -w) zakresów)."
