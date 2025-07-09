# #!/usr/bin/env python3
# import os, socket
# from agent_metrics import cpu_pct, mem_pct

# HOST = "0.0.0.0"
# PORT = int(os.getenv("AGENT_PORT", 9999))

# def calc_score() -> int:
#     busy = max(cpu_pct(), mem_pct())
#     return max(1, min(100, int(round(100 - busy))))

# def serve_forever():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         s.bind((HOST, PORT))
#         s.listen(5)
#         print(f"[agent_tcp] listening on {HOST}:{PORT}")
#         while True:
#             conn, _ = s.accept()
#             with conn:
#                 conn.sendall(f"{calc_score()}%\n".encode())

# if __name__ == "__main__":
#     serve_forever()


#!/usr/bin/env python3
"""
Agente TCP para HAProxy – agora com thresholds de CPU:

    • >= 80 %  →  maint 0%   (servidor sai do balanceamento)
    • <= 60 %  →  ready NN%  (volta a receber tráfego)

Lê CPU/MEM isolados por contêiner via agent_metrics (v1 ou v2).
"""

import os, socket, time
from agent_metrics import cpu_pct, mem_pct   # mem_pct só p/ score

HOST = "0.0.0.0"
PORT = int(os.getenv("AGENT_PORT", 9999))

# limiares
CPU_DISABLE = 80    # %
CPU_ENABLE  = 60    # %

_state = "ready"    # ready | maint


def calc_score() -> int:
    """Score livre 1-100 baseado em max(CPU, MEM)."""
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
                cpu_now = cpu_pct()          # uso atual p/ decisão
                if _state == "ready" and cpu_now >= CPU_DISABLE:
                    _state = "maint"
                elif _state == "maint" and cpu_now <= CPU_ENABLE:
                    _state = "ready"

                if _state == "maint":
                    payload = "maint 0%\n"
                else:
                    payload = f"ready {calc_score()}%\n"
                conn.sendall(payload.encode())
                # pequena pausa evita churn violento caso admin faça telnet
                time.sleep(0.02)


if __name__ == "__main__":
    serve_forever()
