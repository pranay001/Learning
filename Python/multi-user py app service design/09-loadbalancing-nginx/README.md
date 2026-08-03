# Module 09 — Load Balancing with NGINX: Spreading Traffic Across Replicas

## Concept

With multiple API container replicas (Module 08), you need something in front deciding which replica
handles each incoming request. **NGINX** is a common, lightweight, battle-tested choice for this.

| Term | Meaning |
|------|---------|
| **Reverse proxy** | A server that sits in front of your app(s) and forwards client requests to them |
| **Upstream** | NGINX's term for the pool of backend servers it load-balances across |
| **Load balancing algorithm** | How NGINX picks which backend gets the next request (round robin, least connections, ip_hash) |
| **Health check** | NGINX (or NGINX Plus / external tooling) skipping backends that are down |
| **Sticky sessions** | Routing the same client to the same backend repeatedly (avoid this — reinforces statelessness from Module 03) |

## Hands-On Lab

### Step 1 — NGINX config for load balancing across your API replicas

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        # least_conn sends the next request to whichever backend has the fewest
        # active connections — usually better than plain round robin under uneven load
        least_conn;

        server api:8000;
        # When scaled via `docker compose up --scale api=3`, Docker's internal DNS
        # round-robins the "api" hostname across replicas automatically as well —
        # but an explicit NGINX upstream gives you finer control (weights, health checks, etc.)
    }

    server {
        listen 80;

        location /health {
            access_log off;
            proxy_pass http://api_backend;
        }

        location / {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts: don't let one slow backend hang a client forever
            proxy_connect_timeout 5s;
            proxy_read_timeout 30s;

            # Basic retry: if a backend is unreachable, try the next one
            proxy_next_upstream error timeout http_502 http_503;
        }
    }
}
```

### Step 2 — Add NGINX to docker-compose.yml (extending Module 08's file)

```yaml
  nginx:
    image: nginx:1.27
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
    restart: unless-stopped
```

Remove the `ports: - "8000:8000"` mapping from the `api` service itself now — clients should only reach
your API through NGINX on port 80, not by bypassing it directly.

### Step 3 — Scale up and verify distribution

```bash
docker compose up --build --scale api=3 -d
```

Add a `/whoami`-style endpoint (from Module 03) to `main.py` if it's not there already, showing container
hostname:

```python
import socket

@app.get("/whoami")
def whoami():
    return {"hostname": socket.gethostname()}
```

Rebuild, then hit the NGINX-facing port repeatedly:

```bash
for i in $(seq 1 12); do curl -s http://localhost/whoami; echo; done
```

You should see requests landing on **different container hostnames**, proving NGINX (combined with
Docker's DNS round robin across the 3 `api` replicas) is distributing load.

### Step 4 — Prove resilience: kill one backend mid-traffic

```bash
docker compose ps   # note one api container's name, e.g. myapp-api-2

# In one terminal, keep sending requests:
while true; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost/whoami; sleep 0.3; done

# In another terminal, stop one replica:
docker stop myapp-api-2
```

Watch the first terminal — you should see continued `200` responses (NGINX's `proxy_next_upstream`
routing around the dead backend), possibly with one or two transient errors depending on timing, rather
than a full outage.

### Step 5 — Rate limiting at the edge (defense in depth alongside Module 07's app-level limiting)

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        location / {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://api_backend;
            # ... (other directives as before)
        }
    }
}
```

Test: fire a rapid burst and confirm some requests get NGINX's `503` before even reaching your app.

## Checkpoint Questions

1. Why is `least_conn` often a better default than plain round robin for endpoints with varying response times (e.g. Module 06's report generation)?
2. Why must the app remain stateless (Module 03) for load balancing across replicas to work correctly?
3. What's the difference between rate limiting at NGINX (this module) vs. at the app level with Redis (Module 07)? Why might you want both?
4. Why did requests continue succeeding after you killed one backend container?

## What's Next

Module 10 replaces manual `docker compose --scale` with Kubernetes, which adds auto-scaling, self-healing,
and rolling deployments.
