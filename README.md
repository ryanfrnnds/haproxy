# HAProxy + Spring Boot com Balanceamento por Uso de CPU/Memória

Este projeto é uma POC completa de balanceamento de carga com **HAProxy + agent-check TCP**, utilizando:

- Spring Boot (Java 11)
- Docker Swarm
- HAProxy com `agent-check` baseado em uso de CPU/Memória
- Imagem base customizada com agente Python monitorando o container

---

## 📁 Estrutura do Projeto

```
haproxy-springboot-agent-poc/
├── springboot-api/             # Projeto Java com Jib
├── java11-agent-base/          # Imagem base com agente supervisado
└── infra/                      # Infraestrutura com Docker Swarm + HAProxy
```

---

## 🚀 Como rodar localmente

### 1. Construa a imagem base com agente
```bash
cd java11-agent-base
docker build -t ryanfrnnds/java11-agent-base:latest .
docker push ryanfrnnds/java11-agent-base:latest  # se for usar no cluster
```

### 2. Construa a imagem da sua API com Jib
```bash
cd springboot-api
mvn compile jib:dockerBuild -Dimage=ryanfrnnds/springboot-api:latest
```

### 3. Inicialize o Swarm (se necessário)
```bash
docker swarm init
```

### 4. Suba a stack com HAProxy e as APIs
```bash
cd infra
docker stack deploy -c docker-compose.yml springtest
```

---

## 🔁 Como funciona

- O `agent_tcp.py` embutido na imagem monitora uso de CPU/MEM do container.
- Se o uso de CPU passar de 80%, o HAProxy desativa a instância com `maint`.
- Quando a carga cai para menos de 60%, a instância volta a receber tráfego.
- O HAProxy se comunica com o agente via `agent-check` na porta `9999`.

---

## 🔬 Testar o balanceamento

1. Acesse:
   ```bash
   curl http://localhost/hello
   ```

2. Simule carga:
   ```bash
   curl http://localhost/cpu
   ```

3. Acesse o painel do HAProxy:
   ```
   http://localhost:8404/stats
   ```

---

## 🧱 Requisitos

- Docker + Docker Swarm
- Maven 3.8+
- Java 11
- Internet para baixar dependências e imagens base

---

Projeto desenvolvido como POC para balanceamento inteligente de APIs containerizadas com HAProxy.