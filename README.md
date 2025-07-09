# POC — Balanceamento Dinâmico com HAProxy + Docker Swarm

> Demonstração de **balanceamento de carga sensível a recursos**, usando
> HAProxy 2.9, Docker Swarm e uma API Flask que publica sua própria
> “saúde” via *agent‑check* TCP (porta 9999).

---

## 1 • Componentes

| Serviço | Imagem / Caminho | Papel |
|---------|------------------|-------|
| **API** | `helloworld-api:latest` (`/api/*.py`) | Rota `GET /` de teste e `agent_tcp.py`, que calcula CPU/RAM do contêiner e envia para o HAProxy. |
| **HAProxy** | `haproxy:2.9` | Escuta **:80**; painel `/stats` em **:8404**. Ajusta o peso dos back‑ends com base no agente. |
| **Swarm** | Docker Desktop | 2 réplicas (alterável em *docker-stack.yml*). |

### Lógica de thresholds

| Situação do contêiner | Agente devolve | Estado no HAProxy |
|-----------------------|----------------|-------------------|
| CPU **≥ 80 %** | `maint 0%` | Linha fica **MAINT** (não recebe tráfego). |
| CPU **≤ 60 %** | `ready NN%` | Volta para **UP** com peso `NN`. |

---

## 2 • Subindo localmente (Docker Desktop)

```bash
git clone <repo>
cd HAProxy-POC-SWARM

# Inicie o Swarm (se ainda não estiver ativo)
docker swarm init

# Construa a imagem da API
docker build -t helloworld-api:latest ./api

# Suba a stack
docker stack deploy -c docker-stack.yml poc
```

*Abra em seguida*  

* Painel HAProxy: <http://localhost:8404/stats>  
* Rota de teste:  <http://localhost/>

---

## 3 • Teste de balanceamento

1. **Descubra o container da réplica 1**

   ```bash
   docker service ps poc_api
   ```

2. **Estresse só essa réplica**

   ```bash
   CID=$(docker ps --filter name=poc_api.1 --format '{{.ID}}')
   docker exec -it $CID stress-ng --cpu 4 --vm 4 --vm-bytes 75% --timeout 90s
   ```

3. **Acompanhe no /stats**

   * `api1` vai para **MAINT / Wght 0/0**  
   * Todo tráfego será redirecionado para `api2`  
   * Após o stress, `api1` volta para **ready** e o peso sobe.

---

## 4 • Estrutura do projeto

```
api/
├─ agent_api.py
├─ agent_tcp.py
├─ agent_metrics.py
├─ entrypoint.sh
├─ requirements.txt
└─ Dockerfile

haproxy/
└─ haproxy.cfg

docker-stack.yml
README.md
```

---

## 5 • Desligando

```bash
docker stack rm poc
docker swarm leave --force   # opcional
```

---

> Feito com ☕ e muita curiosidade.!
