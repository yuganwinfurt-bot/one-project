#!/usr/bin/env bash
# Read-only checks before installing the new site; prints no passwords or keys.
set -u

printf '%s\n' '== Operating system =='
if [ -r /etc/os-release ]; then
  . /etc/os-release
  printf '%s\n' "$PRETTY_NAME"
fi
printf '%s\n' '== Memory and root disk =='
free -h 2>/dev/null || true
df -h / 2>/dev/null || true
printf '%s\n' '== Listening web/service ports =='
ss -lnt 2>/dev/null | awk 'NR == 1 || $4 ~ /:(22|80|443|8000|8020|8030|11434)$/' || true
printf '%s\n' '== Web server and existing agent services =='
for program in nginx caddy apache2; do
  command -v "$program" 2>/dev/null || true
done
systemctl list-units --type=service --state=running --plain --no-legend 2>/dev/null | grep -Ei 'hermes|nginx|caddy|apache|ollama' || true
printf '%s\n' '== Enabled Nginx site names =='
find /etc/nginx/sites-enabled -maxdepth 1 -type l -printf '%f\n' 2>/dev/null || true
printf '%s\n' '== Domain IPv4 results =='
getent ahostsv4 yuganwinfurt.top 2>/dev/null | awk '{print $1}' | sort -u || true
