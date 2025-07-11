#!/usr/bin/env python3
"""
Agente TCP para HAProxy – com exibição de score, nome e hostname.

    • >= 80 % CPU  →  maint
    • <= 60 % CPU  →  ready
"""

import os, socket, time
from agent_metrics import cpu_pct, mem_pct

HOST = "0.0.0.0"
PORT = int(os.getenv("AGENT_PORT", 9999))

CPU_DISABLE = 80    # % para entrar em manutenção
CPU_ENABLE  = 60    # % para voltar

_state = "ready"
NAME = os.getenv("API_NAME", "api-unknown")
HOSTNAME = socket.gethostname()


def calc_score() -> int:
    """Score livre de 1 a 100, baseado em CPU/MEM do contêiner."""
    busy = max(cpu_pct(), mem_pct())
    return max(1, min(100, int(round(100 - busy))))


def serve_forever() -> None:
    global _state
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"[agent_tcp] listening on {HOST}:{PORT}")
        while True:
            conn, _ = s.accept()
            with conn:
                cpu_now = cpu_pct()
                score = calc_score()

                if _state == "ready" and cpu_now >= CPU_DISABLE:
                    _state = "maint"
                elif _state == "maint" and cpu_now <= CPU_ENABLE:
                    _state = "ready"

                # Mensagem detalhada com nome e hostname
                payload = f"{_state} {score}% name={NAME} host={HOSTNAME}\n"
                conn.sendall(payload.encode())

                time.sleep(0.02)


if __name__ == "__main__":
    serve_forever()
