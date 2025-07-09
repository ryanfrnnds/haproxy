# HAProxy-POC-SWARM

> **Goal:** Demonstrate **dynamic, resource-aware load‑balancing** with  
> Docker Swarm + HAProxy 2.9 + a tiny Flask API that reports its own CPU/RAM
> health through an **agent‑check** on port 9999.

---

## 1 • What you’ll run

| Component | Image / Path | Role |
|-----------|--------------|------|
| **API container** | `helloworld-api:latest` (`/api/*.py`) | Flask “Hello World”, plus `agent_tcp.py` (scores node health → HAProxy). |
| **HAProxy** | `haproxy:2.9` | Front‑end on **:80**, `/stats` on **:8404**. Balances between API replicas using agent weight. |
| **Docker Swarm** | local Desktop | Two replicas (`replicas: 2`, editable in *docker-stack.yml*). |

**CPU thresholds**

* `CPU ≥ 80 %` → replica goes **MAINT** (`maint 0%`) – HAProxy sends 0 requests.  
* `CPU ≤ 60 %` → replica returns **READY NN %** – weight set to *NN*.

---

## 2 • Quick start (local Docker Desktop)

```bash
git clone <this-repo-url>
cd HAProxy-POC-SWARM

# 1) Enable Swarm
docker swarm init

# 2) Build API image
docker build -t helloworld-api:latest ./api

# 3) Deploy stack
docker stack deploy -c docker-stack.yml poc
docker service ls             # watch services start
```

### Dashboards

| URL | What you’ll see |
|-----|-----------------|
| `http://localhost:8404/stats` | HAProxy live stats (no auth for POC). |
| `http://localhost/`           | “Hello World from &lt;slot&gt;!”. |

---

## 3 • Try dynamic weighting

```bash
# find replica 1
docker service ps poc_api

# stress only replica 1
docker exec -it <container‑ID>   stress-ng --cpu 4 --vm 4 --vm-bytes 75% --timeout 60s
```

Open `/stats`; `api1` flips to **MAINT** (Wght 0/0) and all traffic goes to `api2`.
When CPU falls ≤ 60 %, `api1` returns to **READY** and traffic normalizes.

---

## 4 • Repo layout

```
api/
├─ agent_api.py
├─ agent_metrics.py
├─ agent_tcp.py
├─ entrypoint.sh
├─ requirements.txt
└─ Dockerfile
haproxy/
└─ haproxy.cfg
docker-stack.yml
README.md
```

---

## 5 • Key HAProxy backend

```haproxy
backend apis
    server-template api 1-10 tasks.api:5000 weight 100 \
        agent-check agent-port 9999 agent-inter 2s \
        check inter 2s rise 2 fall 3
```

`ready 91%` → Wght 91   |   `maint 0%` → server in MAINT (no LB).

---

## 6 • Tear down

```bash
docker stack rm poc
docker swarm leave --force
```

---

## 7 • Troubleshooting

| Symptom | Fix |
|---------|-----|
| Wght stuck at 100/100 | Ensure :9999 replies “ready NN%” – test with `cat /dev/tcp/IP/9999`. |
| Replica stays MAINT | CPU still above 60 %; wait or lower thresholds. |
| ImportError agent_metrics | Ensure file copied into image; rebuild `--no-cache`. |

Made with ☕ by &lt;your‑team&gt;.
