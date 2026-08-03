# Module 10 — Kubernetes: Auto-Scaling and Self-Healing in Production

## Concept

Kubernetes (K8s) automates what you were doing manually in Modules 08-09: running multiple replicas,
load balancing across them, restarting failed containers, and scaling based on real load.

| Term | Meaning |
|------|---------|
| **Pod** | The smallest deployable unit — one or more containers sharing network/storage |
| **Deployment** | Declares desired state (e.g. "run 3 replicas of this image") — K8s continuously reconciles reality to match |
| **Service** | A stable network endpoint that load-balances across matching pods (like NGINX's upstream, but built-in) |
| **ConfigMap / Secret** | Externalized configuration/credentials, injected into pods as env vars |
| **HPA (Horizontal Pod Autoscaler)** | Automatically adds/removes replicas based on CPU/memory/custom metrics |
| **Liveness / Readiness probe** | K8s equivalent of Docker's HEALTHCHECK — restarts unhealthy pods, and withholds traffic from not-yet-ready pods |
| **Rolling update** | Deploys new versions gradually, keeping the service available throughout |

## Hands-On Lab

### Step 1 — Set up a local Kubernetes cluster

```bash
# Option A: Docker Desktop → Settings → Kubernetes → Enable
# Option B: minikube
minikube start
kubectl get nodes   # should show a Ready node
```

### Step 2 — Build the image and make it available to the cluster

If using minikube:

```bash
eval $(minikube docker-env)
docker build -t learning-api:v1 .
```

### Step 3 — Define the Deployment and Service

Create `k8s/api-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: learning-api
  template:
    metadata:
      labels:
        app: learning-api
    spec:
      containers:
        - name: api
          image: learning-api:v1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                configMapKeyRef:
                  name: api-config
                  key: database_url
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: api-config
                  key: redis_url
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: learning-api
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
```

Create `k8s/config.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  database_url: "postgresql+asyncpg://appuser:apppass@postgres-service:5432/appdb"
  redis_url: "redis://redis-service:6379/0"
```

### Step 4 — Deploy

```bash
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/api-deployment.yaml

kubectl get pods            # should show 3 Running pods
kubectl get deployments
kubectl get services
```

Access the service:

```bash
# minikube:
minikube service api-service --url
# Docker Desktop K8s: the LoadBalancer type will map to localhost automatically, or use:
kubectl port-forward service/api-service 8080:80
curl http://localhost:8080/health
```

### Step 5 — Prove self-healing

```bash
kubectl get pods    # note a pod name, e.g. api-deployment-7d9f8c-abcde
kubectl delete pod api-deployment-7d9f8c-abcde
kubectl get pods    # watch a new pod get created automatically to maintain replicas: 3
```

### Step 6 — Prove readiness probes prevent traffic to unready pods

Temporarily break `/health` (e.g. make it sleep 10s before responding, or return a 500), rebuild, and
apply a rolling update:

```bash
kubectl set image deployment/api-deployment api=learning-api:v2
kubectl rollout status deployment/api-deployment
```

Observe that Kubernetes won't route traffic to new pods until they pass the readiness probe, and won't
kill old pods until new ones are confirmed ready — a zero-downtime rollout.

### Step 7 — Auto-scale based on CPU load

```bash
kubectl autoscale deployment api-deployment --cpu-percent=50 --min=2 --max=8
kubectl get hpa
```

Generate load (reuse Locust from Module 03 or a simple loop) against `/work` (a CPU-heavy endpoint) and
watch:

```bash
kubectl get hpa -w
kubectl get pods -w
```

You should see replica count climb as CPU usage crosses 50%, then scale back down once load subsides.

### Step 8 — Rolling back a bad deployment

```bash
kubectl rollout undo deployment/api-deployment
kubectl rollout status deployment/api-deployment
```

## Checkpoint Questions

1. What's the difference between a liveness probe failing vs. a readiness probe failing — what does K8s do differently in each case?
2. Why does a `Deployment` with `replicas: 3` behave like an automated version of Module 08's manual `--scale api=3`, plus more?
3. Why do resource `requests`/`limits` matter for the scheduler and for the HPA?
4. If a pod keeps crash-looping, what would you check first? (Hint: `kubectl logs`, `kubectl describe pod`)

## What's Next

Now that you can run many replicas that scale automatically, Module 11 covers actually observing what's
happening across all of them — logs, metrics, and tracing.
