# GraceDB Helm Charts — Notes for Claude Code

## Repository layout
The GraceDB helm chart lives in the `gracedb/` subdirectory:
```
gracedb-helm-charts/
└── gracedb/          ← the chart (Chart.yaml, values.yaml, templates/, ...)
    ├── values.yaml       production defaults
    └── values-k3d.yaml   k3d dev overrides (committed here)
```
All `helm` commands should be run from inside `gracedb/`.

## Deploy to the local k3d cluster
The sibling repo `gracedb-server`'s SessionStart hook creates a k3d cluster
named `$K3D_CLUSTER_NAME` and writes kubeconfig to `$KUBECONFIG`.

```bash
# 1. Build and import the server image (run from gracedb-server repo)
(cd /workspace/gracedb-server && docker build -t gracedb-server:dev .)
k3d image import gracedb-server:dev -c "$K3D_CLUSTER_NAME"

# 2. Install / upgrade
cd /workspace/gracedb-helm-charts/gracedb
helm dependency update .
helm upgrade --install gracedb . \
  --values values.yaml \
  --values values-k3d.yaml \
  --create-namespace --namespace gracedb \
  --wait --timeout 10m
```

## values-k3d.yaml is the dev override
It disables Traefik, cert-manager, and Shibboleth (`sandboxed.enabled: true`),
pins the image to the locally-imported tag, and shrinks resource requests to
fit the sandbox. Edit it here and commit; do not modify `values.yaml`.

## Key chart behaviours
- **Shibboleth** is only deployed when `sandboxed.enabled: false`. It is OFF
  for k3d.
- **Traefik** is the ingress controller. It is disabled for k3d; access the
  app via `kubectl port-forward` instead.
- **PostgreSQL** is an in-chart StatefulSet (not a Bitnami subchart) when
  `distributed.enabled: false`. The image is configured under `postgres.image`.
- **Memcached** (not Redis) is used for caching. It is always deployed.
- **`tier.settingModule`** controls `DJANGO_SETTINGS_MODULE` inside the pod.
  For k3d this is set to `config.settings.container.dev`.

## Verifying
```bash
kubectl -n gracedb get pods
kubectl -n gracedb logs -l app.kubernetes.io/name=gracedb --tail=100
kubectl -n gracedb port-forward svc/gracedb 8000:80 &
curl -fs http://localhost:8000/
```

## Resource reality
Sandbox ceiling is ~4 vCPU / 16 GB RAM. Keep `gracedb.gunicorn.worker: 2`
and the memory limits in `values-k3d.yaml` conservative. OOMKilled pods means
tighten further.

## Conventions

### Branch strategy
`main` is a one-way mirror from git.ligo.org. Any commit pushed directly to
`main` will be silently overwritten by the next mirror push from GitLab.

Claude sessions **must not** target `main` for merges or direct pushes.

Instead:
1. Do all work on a short-lived feature branch (e.g. `claude/<topic>`).
2. When the work is ready, merge the feature branch into **`claude-code`**.
   `claude-code` is the durable integration branch that accumulates all
   Claude-produced changes. It is never overwritten by the mirror.
3. The maintainer periodically cherry-picks or pulls commits from `claude-code`
   into the upstream GitLab repository.

Summary: `claude/<topic>` → merge into `claude-code` → maintainer pulls to GitLab.
Never merge into `main`.

### Other conventions
- `values-k3d.yaml` is Claude Code specific; it is safe to modify freely.
- Don't modify `values.yaml` unless the change belongs in production too.
- Keep commits small and descriptive — they will be cherry-picked to GitLab.
