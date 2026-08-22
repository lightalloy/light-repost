#!/usr/bin/env bash
# Локальный запуск с перезапуском при изменении app/ (hot reload).
# Не для Docker/VPS.
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON=python
WATCHFILES=watchfiles
if [[ -x .venv/bin/python ]]; then
  PYTHON=.venv/bin/python
fi
if [[ -x .venv/bin/watchfiles ]]; then
  WATCHFILES=.venv/bin/watchfiles
elif ! command -v watchfiles >/dev/null 2>&1; then
  echo "watchfiles не найден. Установи dev-зависимости:" >&2
  echo "  source .venv/bin/activate && pip install -r requirements-dev.txt" >&2
  exit 1
fi

exec "$WATCHFILES" --filter python "$PYTHON -m app.main" app
