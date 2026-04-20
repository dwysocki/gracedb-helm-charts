# GraceDB Helm Charts — Notes for Claude Code

## Repository layout
This repo is a GitHub mirror of `git.ligo.org/computing/gracedb/k8s/helm`.
The GraceDB helm chart lives in the `gracedb/` subdirectory:
```
<this repo>/
└── gracedb/          ← the chart (Chart.yaml, values.yaml, templates/, ...)
    ├── values.yaml       production defaults
    └── values-k3d.yaml   k3d dev overrides (committed here)
```
All `helm` commands should be run from inside `gracedb/`.

## Environment compatibility
The Claude Code **web** environment (claude.ai/code) runs inside a **gVisor**
sandbox. gVisor does not expose the kernel interfaces required by container
orchestrators:

| Requirement | gVisor status | Effect |
|---|---|---|
| iptables / nftables | unsupported | Docker daemon cannot start; k3d fails |
| overlay filesystem | unsupported | containerd image layers fail |
| cgroup rootfs (`/sys/fs/cgroup`) | not fully exposed | kubelet ContainerManager panics |

k3d, k3s (direct), and Podman-backed Kubernetes all fail in this environment.
The SessionStart hook in `gracedb-server` detects gVisor and skips the cluster
step automatically, printing a clear warning.

If you need the full Kubernetes stack, run Claude Code locally (CLI or IDE
extension) on a Linux host with kernel ≥ 5.4 and Docker installed.

## Deploy to the local k3d cluster
The sibling repo `gracedb-server`'s SessionStart hook creates a k3d cluster
named `$K3D_CLUSTER_NAME` and writes kubeconfig to `$KUBECONFIG`.

```bash
# 1. Build and import the server image (run from gracedb-server repo)
(cd ../gracedb-server && docker build -t gracedb-server:dev .)
k3d image import gracedb-server:dev -c "$K3D_CLUSTER_NAME"

# 2. Install / upgrade
cd "$CLAUDE_PROJECT_DIR/gracedb"
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
This repo is mirrored one-way from `git.ligo.org/computing/gracedb/k8s/helm`.
Mirror pushes overwrite any branch that also exists upstream. The only
branches safe from overwrite are those that do not exist in that GitLab repo.

All Claude work **must** stay on branches prefixed with `claude/`. These
branches are not present upstream and will never be clobbered by a mirror push.

- **Never push to, or open PRs targeting, any branch without a `claude/` prefix.**
- Feature branches follow the pattern `claude/<workspace>`, where `<workspace>`
  describes the task (e.g. `claude/fix-chart-resources`).
- **At the start of each session, ask the user what workspace name to use.**
  Claude will then work on `claude/<workspace>` for that session.
- Completed feature branches are merged into a `claude/` integration branch
  agreed with the maintainer (e.g. `claude/initial_claude_setup`). The
  maintainer cherry-picks from there into the upstream GitLab repo.

### Other conventions
- `values-k3d.yaml` is Claude Code specific; it is safe to modify freely.
- Don't modify `values.yaml` unless the change belongs in production too.
- Keep commits small and descriptive — they will be cherry-picked to GitLab.
