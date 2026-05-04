# Deployment

Live at **https://qrouter.ask-meridian.uk/** — the FastAPI HTTP wrapper
(`src/qrouter/http_server.py`) running under systemd on `meridian-vm`,
fronted by the existing `meridian` Cloudflare Tunnel.

```
   ┌─────────────────────────────┐         ┌──────────────────────────┐
   │  qrouter.ask-meridian.uk    │  CNAME  │  Cloudflare Tunnel        │
   │  (Cloudflare DNS, proxied)  │ ──────► │  "meridian"               │
   └─────────────────────────────┘         │  (4 healthy connectors)   │
                                            └────────────┬─────────────┘
                                                         │ ingress
                                                         ▼
                                            ┌──────────────────────────┐
                                            │  meridian-vm             │
                                            │  127.0.0.1:8004 ─►       │
                                            │  systemd unit            │
                                            │    qrouter.service       │
                                            │    /opt/qrouter/.venv/   │
                                            │    bin/uvicorn …         │
                                            └──────────────────────────┘
```

The same tunnel also serves `vault.ask-meridian.uk → 127.0.0.1:8003`.
Two unrelated services, one connector deployment — keeps ops surface
small.

## How the service was set up

```bash
# 1. Code on the VM
mkdir -p /opt/qrouter
git clone https://github.com/LuuOW/qrouter /opt/qrouter   # (or rsync from local)

# 2. venv with runtime-only deps (FastAPI + uvicorn + numpy)
python3 -m venv /opt/qrouter/.venv
/opt/qrouter/.venv/bin/pip install -e /opt/qrouter

# 3. systemd unit at /etc/systemd/system/qrouter.service (in repo: ops/qrouter.service)
systemctl daemon-reload
systemctl enable --now qrouter.service

# 4. Cloudflare side — ingress rule + DNS CNAME (one-time, via API)
#    Tunnel ingress now contains:
#      vault.ask-meridian.uk   → http://127.0.0.1:8003
#      qrouter.ask-meridian.uk → http://127.0.0.1:8004    ← NEW
#      http_status:404
#    DNS: qrouter.ask-meridian.uk CNAME <tunnel-id>.cfargotunnel.com (proxied)

# 5. Verify
curl https://qrouter.ask-meridian.uk/health
```

## Backend modes

`http_server.py` detects whether the QNLP stack is importable on import:

| `BACKEND` value | Meaning                                                      |
|-----------------|--------------------------------------------------------------|
| `stub`          | `lambeq` / `pennylane` not installed. `/rank` returns the    |
|                 | fixture documents in their natural order with `score: 0.0`.  |
|                 | Lets us verify deployment plumbing before the heavy stack.   |
| `lambeq`        | Real DisCoCat → variational circuit → Born-rule overlap.     |

To upgrade from `stub` → `lambeq`:

```bash
# CPU-only torch first to skip the multi-gigabyte CUDA stack on a non-GPU VM
TMPDIR=/var/tmp/pip /opt/qrouter/.venv/bin/pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu torch
# Then the QNLP extras
TMPDIR=/var/tmp/pip /opt/qrouter/.venv/bin/pip install --no-cache-dir \
    /opt/qrouter[qnlp]
# Restart so the new BACKEND is picked up at import time
systemctl restart qrouter
curl -s http://127.0.0.1:8004/health   # → "backend": "lambeq"
```

`TMPDIR=/var/tmp/pip` is required because the default `/tmp` on this VM
is a 477 MB tmpfs and torch's wheel alone is ~750 MB.

## Operational notes

- **No auth on this endpoint.** Open CORS, no rate limiting. Fine for
  the day-1 fixture (5 documents, response is bounded). Once a real
  corpus lands or per-user state appears, gate via API key + per-IP
  rate limit.
- **Logs:** `journalctl -u qrouter -f`
- **Restart:** `systemctl restart qrouter` — service config has
  `Restart=on-failure`, so it self-heals on crashes (5s backoff).
- **Hardening already in the unit:** `NoNewPrivileges`, `ProtectSystem=strict`,
  `ProtectHome`, `PrivateTmp`, `ProtectKernel{Tunables,Modules}`,
  `ProtectControlGroups`. Writable paths limited to `/opt/qrouter`.
