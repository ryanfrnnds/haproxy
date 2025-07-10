FROM eclipse-temurin:11-jdk

# Instala dependências básicas
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-pip supervisor && \
    python3 -m pip install --break-system-packages --no-cache-dir psutil && \
    rm -rf /var/lib/apt/lists/*

# Cria diretórios e copia arquivos
RUN mkdir -p /opt/agent /etc/supervisor
COPY agent_metrics.py /opt/agent/agent_metrics.py
COPY agent_tcp.py /opt/agent/agent_tcp.py
COPY supervisord.conf /etc/supervisor/supervisord.conf
RUN chmod +x /opt/agent/agent_tcp.py

# Usa supervisord como entrypoint
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
