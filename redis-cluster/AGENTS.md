## Learned User Preferences

- Keep `VALKEY_PASSWORD` unset or empty (and no `.env`) to run without `requirepass`/`masterauth`; when auth is enabled, use the same values for Compose and `./create-cluster`.

## Learned Workspace Facts

- This repo runs a six-node Valkey 9 cluster (`valkey/valkey:9-alpine3.23`) on Docker Compose with three primaries and three replicas; `./create-cluster` runs `valkey-cli --cluster create` with `--cluster-replicas 1` (first three endpoints are masters).
- Node data and cluster metadata live under `../volumes/valkey-cluster/valkey-node-*/data` (including `nodes.conf` and AOF); stale disk state can block `--cluster create` until the bootstrap script’s wipe path runs.
- `./create-cluster` considers the cluster healthy only when `cluster_state` is `ok` and `cluster_slots_ok` is `16384`; otherwise it best-effort `FLUSHALL` (replicas may return `READONLY`) then `CLUSTER RESET HARD` on every node before creating the cluster.
- Compose passes `--cluster-require-full-coverage no` as a homelab default; it does not replace a correct full slot assignment.
- Host client ports `7000–7005` and cluster bus ports `17000–17005` are published; host `7000` may conflict with macOS Control Center / AirPlay.
- Services use fixed `container_name` values `valkey-node-0` … `valkey-node-5`. `./create-cluster` bootstraps on `valkey-cluster-net`, then switches announce to `VALKEY_CLUSTER_ANNOUNCE_HOST` (default `host.docker.internal`) with published ports `7000–7005` / bus `17000–17005` and refreshes peer addresses for host hairpin.
- macOS host clients need `127.0.0.1 host.docker.internal` in `/etc/hosts` (`./setup-host-macos`). Host CLI: `valkey-cli -c -h 127.0.0.1 -p 7000`; seed URL uses `VALKEY_CLUSTER_DNS` / `VALKEY_CLUSTER_SEED_PORT`.
