#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f prometheus.yml ]; then echo 'Execute montar_monitoramento.sh primeiro.'; exit 1; fi
BACKUP="$(mktemp)"
cp prometheus.yml "$BACKUP"
restore() {
  cp "$BACKUP" prometheus.yml
  rm -f "$BACKUP"
  docker compose restart prometheus >/dev/null 2>&1 || true
  echo 'Alvo original restaurado no Prometheus.'
}
trap restore EXIT INT TERM
python3 - <<'PY2'
from pathlib import Path
p=Path('prometheus.yml')
s=p.read_text()
s=s.replace('zelabairro-gs2026-mathh.onrender.com:443', '127.0.0.1:1')
if "127.0.0.1:1" not in s: raise SystemExit('Alvo esperado não encontrado. Não alterei o arquivo.')
p.write_text(s)
PY2
docker compose restart prometheus
printf '\nAlvo LOCAL de teste com scrape inválido, aplicação pública continua online.\n'
printf 'Abra http://127.0.0.1:9090/alerts e capture Firing depois do período for: 30s.\n'
read -r -p 'Depois de obter o print, pressione Enter para restaurar o alvo: ' _
