# Projeto de POC - HAProxy com Agente Dinâmico

Este projeto é uma prova de conceito (POC) que demonstra como utilizar o HAProxy em conjunto com um agente customizado para balanceamento de carga baseado em consumo de CPU. A estrutura está dividida em três diretórios principais:

---

## 📁 `infra/`

Contém os arquivos de configuração para subir o ambiente completo com Docker Swarm:

- `docker-compose.yml`: orquestra os serviços (HAProxy, APIs, agentes).
- `haproxy.cfg`: configuração dinâmica do HAProxy com suporte a `agent-check` via porta TCP 9999.
- Rede interna e volumes são definidos aqui.

---

## 📁 `java11-agent-base/`

Imagem base Docker para aplicações Spring Boot com suporte a supervisord e agente customizado:

- **Base:** `eclipse-temurin:11-jdk`
- Instala Python 3, Supervisor e o módulo `psutil`.
- Copia o agente `agent_tcp.py` e configura o `supervisord.conf` para iniciar tanto o agente quanto a aplicação Java.
- **Finalidade:** reutilizável como `FROM` em outras imagens via Jib.

---

## 📁 `springboot-api/`

Exemplo funcional de uma API Spring Boot empacotada com o plugin **Jib**:

- Utiliza a imagem `ryanfrnnds/jib-java11-agent-base:latest` como base.
- Não define `entrypoint`, pois delega isso para o supervisord da imagem base.
- **Aplicação demo**: uma API minimalista configurada para rodar junto ao `agent_tcp.py` no mesmo container.

---

## Como usar

1. Compile e gere a imagem base:
   ```bash
   docker build -t ryanfrnnds/jib-java11-agent-base:latest ./java11-agent-base
   ```

2. Gere a imagem da API usando Jib:
   ```bash
   mvn clean compile jib:dockerBuild -Dimage=ryanfrnnds/springboot-api:latest
   ```

3. Suba a stack completa:
   ```bash
   docker stack deploy -c docker-compose.yml haproxy-poc
   ```

---

## Observações

- O HAProxy usa `agent-check` para decidir se uma instância deve ou não receber tráfego.
- O agente `agent_tcp.py` responde na porta `9999` com "up 100" ou "down 0", dependendo da carga da CPU.
- O supervisord garante que, se a aplicação Spring ou o agente caírem, ambos serão reiniciados automaticamente.

---

## Logs

Para que o log da API continue sendo visível no stdout (ex: para ferramentas como Graylog via Docker logging driver), certifique-se de que o `java` seja iniciado em primeiro plano e seus logs sejam redirecionados corretamente.

---

© ryanfrnnds • 2025