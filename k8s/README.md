# Kubernetes Configuration for ARIA-SDR

## GitLab Agent Setup

### Token Information

- **Agent Token**: `glagent-VggOFD80ebT2VK2VoajgC286MQpwOjE4dTgxMww.01.130rcoyhi`
- **Namespace**: `gitlab-agent-aria`
- **KAS Address**: `wss://kas.gitlab.com`

### Installation Commands

```bash
# Add GitLab Helm repository
helm repo add gitlab https://charts.gitlab.io
helm repo update

# Install GitLab Agent
helm upgrade --install aria gitlab/gitlab-agent \
    --namespace gitlab-agent-aria \
    --create-namespace \
    --set config.token=glagent-VggOFD80ebT2VK2VoajgC286MQpwOjE4dTgxMww.01.130rcoyhi \
    --set config.kasAddress=wss://kas.gitlab.com
```

## ARIA-SDR Kubernetes Manifests

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aria-sdr
  labels:
    name: aria-sdr
    app: aria-sdr
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aria-sdr-config
  namespace: aria-sdr
data:
  PYTHON_VERSION: "3.11"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  API_LOG_LEVEL: "info"
  EMBEDDING_MODEL: "text-embedding-3-small"
  EMBEDDING_DIM: "1536"
  RAG_ENABLE: "true"
  RAG_DEFAULT_SOURCE: "faq"
  VOLUME_ALTO_LIMIAR: "1200"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aria-sdr-secrets
  namespace: aria-sdr
type: Opaque
stringData:
  OPENAI_API_KEY: "sk-..."
  ASSISTANT_ID: "asst-..."
  SUPABASE_URL: "https://..."
  SUPABASE_SERVICE_ROLE_KEY: "..."
  MINDCHAT_API_TOKEN: "..."
  FASTAPI_BEARER_TOKEN: "dtransforma2026"
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aria-sdr
  namespace: aria-sdr
  labels:
    app: aria-sdr
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aria-sdr
  template:
    metadata:
      labels:
        app: aria-sdr
    spec:
      containers:
      - name: aria-sdr
        image: aria-sdr:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: aria-sdr-config
        - secretRef:
            name: aria-sdr-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: aria-sdr-service
  namespace: aria-sdr
spec:
  selector:
    app: aria-sdr
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aria-sdr-ingress
  namespace: aria-sdr
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: api.ar-online.com.br
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: aria-sdr-service
            port:
              number: 80
```

## GitLab CI/CD Integration

### Auto Deploy Configuration

```yaml
# .gitlab-ci.yml - Kubernetes deployment
deploy_k8s:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl apply -f k8s/namespace.yaml
    - kubectl apply -f k8s/configmap.yaml
    - kubectl apply -f k8s/secret.yaml
    - kubectl apply -f k8s/deployment.yaml
    - kubectl apply -f k8s/service.yaml
    - kubectl apply -f k8s/ingress.yaml
    - kubectl rollout status deployment/aria-sdr -n aria-sdr
  environment:
    name: production
    url: https://api.ar-online.com.br
  only:
    - main
  when: manual
```

## Monitoring and Logs

### Prometheus Monitoring

```yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: aria-sdr-monitor
  namespace: aria-sdr
spec:
  selector:
    matchLabels:
      app: aria-sdr
  endpoints:
  - port: http
    path: /metrics
```

### Logging Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aria-sdr-logging
  namespace: aria-sdr
data:
  log-level: "INFO"
  log-format: "json"
```

## Security

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aria-sdr-netpol
  namespace: aria-sdr
spec:
  podSelector:
    matchLabels:
      app: aria-sdr
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
```

### Pod Security Policy

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: aria-sdr-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## Backup and Recovery

### Persistent Volume

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: aria-sdr-pvc
  namespace: aria-sdr
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

## Troubleshooting

### Common Commands

```bash
# Check pods
kubectl get pods -n aria-sdr

# Check logs
kubectl logs -f deployment/aria-sdr -n aria-sdr

# Check services
kubectl get svc -n aria-sdr

# Check ingress
kubectl get ingress -n aria-sdr

# Port forward for testing
kubectl port-forward svc/aria-sdr-service 8000:80 -n aria-sdr
```

### Health Checks

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics
```

---

**ARIA-SDR** - Deploying AI agents to Kubernetes 🚀☸️
