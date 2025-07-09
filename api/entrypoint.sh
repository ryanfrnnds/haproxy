#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Entrypoint para o container:
#   1. Inicia agente TCP em $AGENT_PORT (padrão 9999) → usado pelo agent-check
#   2. Inicia Gunicorn (ou servidor Flask nativo) em $PORT (padrão 5000)
# -----------------------------------------------------------------------------
set -euo pipefail

PORT="${PORT:-5000}"
AGENT_PORT="${AGENT_PORT:-9999}"
APP_MODULE="agent_api:app"


# ── Inicia agente TCP no background ────────────────────────
python agent_tcp.py &
TCP_PID=$!
echo "[entrypoint] Agent TCP started (pid=$TCP_PID) on port $AGENT_PORT"

# ── Calcula workers se não vier no env ─────────────────────
if [[ -z "${WORKERS:-}" ]]; then
  WORKERS=$(python - <<'PY'
import multiprocessing, math
print(max(1, math.floor(multiprocessing.cpu_count() * 2 + 1)))
PY
)
fi

# ── Lança Gunicorn ou Flask dev server ─────────────────────
if command -v gunicorn >/dev/null 2>&1; then
  echo "[entrypoint] Starting Gunicorn — workers=$WORKERS port=$PORT"
  exec gunicorn --workers "$WORKERS" --bind "0.0.0.0:${PORT}" "$APP_MODULE"
else
  echo "[entrypoint] Gunicorn not found, falling back to Flask dev server (not recommended for prod)"
  exec python agent_api.py
fi
