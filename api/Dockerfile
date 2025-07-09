##############################
# Dockerfile – agent API     #
##############################

FROM python:3.11-slim

# ── Dependências do sistema ────────────────────────────────────────────
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential gcc \
        stress-ng netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# ── Usuário não-root ───────────────────────────────────────────────────
ENV USER=appuser \
    HOME=/home/appuser
RUN adduser --disabled-password --gecos "" $USER

# ── Instalação de dependências Python ─────────────────────────────────
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Código da aplicação ───────────────────────────────────────────────
COPY . .

# Diretório gravável para stress-ng e logs
RUN chown -R $USER:$USER /app

# ── Exposição de portas & variáveis padrão ────────────────────────────
EXPOSE 5000 9999
ENV PORT=5000 \
    AGENT_PORT=9999 \
    API_NAME=api-docker

# ── Entrypoint ─────────────────────────────────────────────────────────
RUN chmod +x entrypoint.sh
USER $USER
ENTRYPOINT ["./entrypoint.sh"]
