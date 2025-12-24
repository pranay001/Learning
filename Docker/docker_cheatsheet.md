
# 🐳 Docker Cheat Sheet (Extended)

A **detailed, reference-style Docker cheat sheet** covering:
- Docker CLI
- Container lifecycle & naming
- Volumes & networking
- **Dockerfile (deep dive)**
- **Docker Compose (deep dive)**

Designed to be used as a **day-to-day reference**.

---

# 1️⃣ Docker Basics

## Core Concepts
- **Image**: Immutable template (like a class)
- **Container**: Runtime instance of an image (like an object)
- **Dockerfile**: Build recipe for images
- **Volume**: Persistent data storage
- **Network**: Virtual LAN for containers

Mental model:
```
Dockerfile → Image → Container
```

---

# 2️⃣ Docker CLI Essentials

```bash
docker --version
docker info
```

---

# 3️⃣ Images

```bash
docker pull centos:7
docker images
docker rmi centos:7
```

---

# 4️⃣ Containers

## Run
```bash
docker run -it centos:7 /bin/bash
docker run -d centos:7 sleep infinity
```

## List
```bash
docker ps
docker ps -a
```

## Stop / Start / Restart
```bash
docker stop <container>
docker start <container>
docker restart <container>
```

---

# 5️⃣ Naming Containers (`--name`)

```bash
docker run --name my-centos centos:7
docker run --name=my-centos centos:7
```

**Recommended:** `--name my-centos`

### Rename
```bash
docker rename old_name new_name
```

### Naming Rules
- lowercase only
- numbers allowed
- `-` and `_` allowed
- no spaces

Best practice:
```
<project>-<service>-<purpose>
```

---

# 6️⃣ Exec, Logs, Inspect

```bash
docker exec -it my-centos /bin/bash
docker logs my-centos
docker logs -f my-centos
docker inspect my-centos
```

---

# 7️⃣ Copy Files

```bash
docker cp file.txt my-centos:/root/
docker cp my-centos:/root/out.log .
```

---

# 8️⃣ Volumes & Mounts

## Named Volumes
```bash
docker volume create mydata
docker run -v mydata:/data centos:7
```

## Bind Mounts
```bash
docker run -v C:\myfiles:/workspace centos:7
```

---

# 9️⃣ Port Mapping

```bash
docker run -p 5901:5901 centos
docker port my-centos
```

---

# 🧱 Dockerfile – Deep Dive

A Dockerfile defines **how an image is built**.

---

## Dockerfile Execution Model

- Instructions execute **top to bottom**
- Each instruction creates a **layer**
- Layers are cached

Implication:
- Put **rarely changing steps first**
- Frequently changing steps last

---

## Common Instructions

### FROM (mandatory)
```Dockerfile
FROM centos:7
```

### WORKDIR
```Dockerfile
WORKDIR /app
```

### RUN (build-time)
```Dockerfile
RUN yum update -y &&     yum install -y vim net-tools &&     yum clean all
```

### COPY vs ADD
```Dockerfile
COPY . /app
```
Use `COPY` unless you explicitly need `ADD` features.

### ENV
```Dockerfile
ENV MODE=production
```

### EXPOSE
```Dockerfile
EXPOSE 8080
```
Documentation only (does not publish ports).

---

## CMD vs ENTRYPOINT (Critical)

### CMD (overridable)
```Dockerfile
CMD ["/bin/bash"]
```

### ENTRYPOINT (fixed)
```Dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
```

Best practice:
- ENTRYPOINT → executable
- CMD → arguments

---

## Multi-stage Builds (Important)

```Dockerfile
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN go build -o app

FROM alpine:3.19
COPY --from=builder /app/app /app/app
CMD ["/app/app"]
```

Benefits:
- Smaller images
- Better security

---

## Build Image

```bash
docker build -t myimage:1.0 .
```

Avoid:
```text
latest
```

---

## Common Dockerfile Mistakes

- Too many layers
- Using `latest`
- Running everything as root
- Installing unnecessary packages

---

# 🧩 Docker Compose – Deep Dive

Docker Compose defines **how containers run together**.

---

## When to Use Compose

- Multi-container systems
- Reproducible environments
- Local dev & CI

---

## Compose File Structure

```yaml
version: "3.9"

services:
  app:

volumes:
networks:
```

---

## Service Definition

```yaml
services:
  app:
    image: myapp
    container_name: myapp-dev
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data
    environment:
      MODE: dev
    depends_on:
      - db
    restart: unless-stopped
```

---

## Key Compose Fields

### image / build
- `image`: use prebuilt image
- `build`: build from Dockerfile

### ports
Same as `-p`

### volumes
Persistent data

### environment
Runtime variables

### depends_on
Startup order (not readiness)

### restart
- no
- always
- unless-stopped

---

## Compose Networking (Very Important)

- One network per compose project
- Service name = DNS hostname

Example:
```yaml
db:
  image: mysql

app:
  image: myapp
```
Inside `app`:
```
db:3306
```

---

## Docker Compose Commands

```bash
docker compose up
docker compose up -d
docker compose down
docker compose ps
docker compose logs -f
docker compose build
```

---

## docker run vs docker compose

| docker run | docker compose |
|----------|----------------|
| Single container | Multi-container |
| CLI based | YAML based |
| Hard to reproduce | Version controllable |
| Manual networking | Automatic networking |

---

# 🧠 Final Mental Models

```
Dockerfile → builds IMAGE
docker run → runs CONTAINER
docker compose → orchestrates CONTAINERS
```

---

# ✅ Best Practices Summary

- Name containers
- Avoid `latest`
- Use volumes
- One process per container
- Keep Dockerfiles small
- Version control compose files

---

Happy Dockering 🐳
