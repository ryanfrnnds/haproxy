#!/bin/bash
set -e

echo "[agent] Iniciando supervisord..."
supervisord -c /opt/agent/supervisord.conf &

sleep 1
echo "[agent] Iniciando aplicação Java..."
exec java $JAVA_OPTS -jar /app/app.jar