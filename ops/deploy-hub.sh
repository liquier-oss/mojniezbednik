#!/usr/bin/env bash
# Wdrożenie mojniezbednik.pl - uruchamiane przez GitHub Actions.
# Klucz SSH użytkownika "deploy" ma wymuszoną komendę = ten skrypt,
# więc GitHub nie może na serwerze zrobić nic innego.
# Instalowany jako root do /usr/local/sbin/mojniezbednik-deploy (nie do edycji przez repo).
set -euo pipefail

REPO=/home/deploy/mojniezbednik
SITE=/var/www/hub
BACKUP=/home/deploy/hub-poprzednia

exec 9>/tmp/mojniezbednik-deploy.lock
flock -n 9 || { echo "Wdrożenie już trwa."; exit 1; }

cd "$REPO"
git fetch --quiet origin main
git reset --hard --quiet origin/main
echo "Wersja: $(git log -1 --oneline)"

# Kopia obecnej strony na wypadek błędu
mkdir -p "$BACKUP"
rsync -a --delete "$SITE/" "$BACKUP/"

if python3 update_hub.py && [ -s "$SITE/index.html" ]; then
  echo "OK: strona wygenerowana $(date '+%F %T')"
else
  echo "BŁĄD generatora - przywracam poprzednią wersję strony." >&2
  rsync -a --delete "$BACKUP/" "$SITE/"
  exit 1
fi
