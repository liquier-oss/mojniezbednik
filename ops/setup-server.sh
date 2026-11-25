#!/usr/bin/env bash
# Jednorazowa konfiguracja VPS (Ubuntu + nginx) dla mojniezbednik.pl
# Uruchom:  sudo bash ops/setup-server.sh ~/deploy_key.pub
# Skrypt jest ostrożny: nie wyłączy logowania hasłem, jeśli nie masz klucza SSH,
# i nie włączy firewalla bez otwartego portu SSH.
set -euo pipefail

WEB_ROOT="${WEB_ROOT:-/var/www/hub}"
DEPLOY_PUB="${1:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"

[ "$(id -u)" -eq 0 ] || { echo "Uruchom przez sudo."; exit 1; }
[ -d "$WEB_ROOT" ]  || { echo "Nie ma katalogu $WEB_ROOT. Ustaw WEB_ROOT=... i uruchom ponownie."; exit 1; }
[ -f "$DEPLOY_PUB" ] || { echo "Podaj ścieżkę do klucza publicznego deploy (.pub)."; exit 1; }

echo ">> 1/7 Aktualizacja i pakiety"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get -yq upgrade
apt-get -yq install unattended-upgrades fail2ban ufw rsync curl git

echo ">> 2/7 Automatyczne łatki bezpieczeństwa"
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF
systemctl enable --now unattended-upgrades

echo ">> 3/7 fail2ban (blokada zgadywania haseł SSH)"
cat > /etc/fail2ban/jail.local <<'EOF'
[sshd]
enabled  = true
backend  = systemd
maxretry = 3
findtime = 1h
bantime  = 1d
bantime.increment = true
EOF
systemctl enable --now fail2ban
systemctl restart fail2ban

echo ">> 4/7 Użytkownik 'deploy' (może tylko uruchomić wdrożenie)"
id deploy &>/dev/null || useradd -m -s /bin/bash deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
install -m 755 -o root -g root "$HERE/deploy-hub.sh" /usr/local/sbin/mojniezbednik-deploy
# Klucz GitHub Actions -> serwer: wolno mu TYLKO uruchomić skrypt wdrożenia
echo "command=\"/usr/local/sbin/mojniezbednik-deploy\",restrict $(cat "$DEPLOY_PUB")" > /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
# Klucz serwer -> GitHub (tylko odczyt repo), do dodania jako "Deploy key"
if [ ! -f /home/deploy/.ssh/github_ro ]; then
  ssh-keygen -q -t ed25519 -N "" -C "vps-read-only" -f /home/deploy/.ssh/github_ro
fi
cat > /home/deploy/.ssh/config <<'EOF2'
Host github.com
  IdentityFile ~/.ssh/github_ro
  IdentitiesOnly yes
EOF2
ssh-keyscan -t ed25519 github.com > /home/deploy/.ssh/known_hosts 2>/dev/null
chown -R deploy:deploy /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/config
# Strona należy do deploy (generator ją nadpisuje), nginx tylko czyta
chown -R deploy:deploy "$WEB_ROOT"
find "$WEB_ROOT" -type d -exec chmod 755 {} +
find "$WEB_ROOT" -type f -exec chmod 644 {} +

echo ">> 5/7 SSH"
# SSH_PASSWORD_LOGIN=no wyłącza hasła (tylko klucze). Domyślnie hasła zostają włączone.
SSH_PASSWORD_LOGIN="${SSH_PASSWORD_LOGIN:-yes}"
ADMIN="${SUDO_USER:-ubuntu}"; [ "$ADMIN" = root ] && ADMIN=ubuntu
ADMIN_HOME=$(getent passwd "$ADMIN" | cut -d: -f6)
if [ "$SSH_PASSWORD_LOGIN" = "no" ] && [ ! -s "$ADMIN_HOME/.ssh/authorized_keys" ]; then
  echo "   $ADMIN nie ma klucza SSH - zostawiam logowanie hasłem."
  SSH_PASSWORD_LOGIN=yes
fi
# Plik 00- wczytuje się przed 50-cloud-init.conf, więc jego ustawienia wygrywają
rm -f /etc/ssh/sshd_config.d/99-hardening.conf
cat > /etc/ssh/sshd_config.d/00-hardening.conf <<EOF
PasswordAuthentication $SSH_PASSWORD_LOGIN
KbdInteractiveAuthentication no
PermitRootLogin no
MaxAuthTries 3
LoginGraceTime 30
AllowUsers $ADMIN deploy
X11Forwarding no
EOF
if sshd -t; then
  systemctl reload ssh
  echo "   SSH: hasła=$SSH_PASSWORD_LOGIN, root wyłączony, dozwoleni: $ADMIN, deploy."
else
  rm -f /etc/ssh/sshd_config.d/00-hardening.conf
  echo "   Błąd konfiguracji SSH - cofnięto zmianę."
fi

echo ">> 6/7 Firewall"
SSH_PORT=$(sshd -T 2>/dev/null | awk '/^port /{print $2}' | head -n1 || true)
SSH_PORT=${SSH_PORT:-22}
ufw default deny incoming
ufw default allow outgoing
ufw allow "$SSH_PORT"/tcp comment ssh
# usuń ogólne reguły www, jeśli istnieją - www będzie tylko z Cloudflare
ufw --force delete allow 'Nginx Full' 2>/dev/null || true
ufw --force delete allow 'Nginx HTTP' 2>/dev/null || true
ufw --force delete allow 'Nginx HTTPS' 2>/dev/null || true
ufw --force delete allow 80/tcp 2>/dev/null || true
ufw --force delete allow 443/tcp 2>/dev/null || true
ufw --force delete allow 80 2>/dev/null || true
ufw --force delete allow 443 2>/dev/null || true
ufw --force enable
install -m 750 "$HERE/cloudflare-only.sh" /usr/local/sbin/cloudflare-only.sh
/usr/local/sbin/cloudflare-only.sh

echo ">> 7/7 Nagłówki nginx i zadania cron"
install -m 644 "$HERE/security-headers.conf" /etc/nginx/snippets/security-headers.conf
install -m 750 "$HERE/audit.sh" /usr/local/sbin/audyt.sh
cat > /etc/cron.d/mojniezbednik <<'EOF'
# Aktualizacja listy IP Cloudflare - poniedziałek 4:17
17 4 * * 1 root /usr/local/sbin/cloudflare-only.sh >/var/log/cloudflare-only.log 2>&1
# Audyt bezpieczeństwa z raportem Claude - codziennie 6:05 (wymaga /etc/audyt.env)
5 6 * * * root [ -f /etc/audyt.env ] && /usr/local/sbin/audyt.sh >/var/log/audyt-cron.log 2>&1
EOF

echo
echo "GOTOWE. Zostało ręcznie (instrukcja w README):"
echo " - dopisać 'include snippets/security-headers.conf;' w konfiguracji strony nginx"
echo " - zainstalować Claude Code i utworzyć /etc/audyt.env"
echo
echo "Klucz do dodania w GitHub -> repo -> Settings -> Deploy keys (BEZ zaznaczania 'Allow write access'):"
cat /home/deploy/.ssh/github_ro.pub
