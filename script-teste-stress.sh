CID=$(docker ps --filter name=haproxy-poc_api.2 --format '{{.ID}}')
docker exec -it "$CID" stress-ng --cpu 4 --vm 4 --vm-bytes 75% --timeout 90s

# 3 – abrir http://<manager>:8404/stats e ver:
#     api1 Wght ↓ ~20/20   |   api2 fica perto de 90/90
