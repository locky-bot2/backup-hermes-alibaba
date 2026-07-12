# Swap Setup for Low-RAM VPS (<2GB)

## When to Use

Any VPS with ≤2GB RAM where you run Node.js build tools (Vite, esbuild, webpack) or Hermes with multiple services (gateway + dashboard + TUI + workspace).

## Why

esbuild (used by Vite for dependency optimization) spawns child processes that can spike memory usage to 1.5GB+. On a 1.8GB RAM VPS with Hermes consuming ~900MB, the OOM killer kills the esbuild process. Symptoms:

- `Error: Error during dependency optimization: The service was stopped` from esbuild
- `vite build` exits with code 130/143 (SIGTERM/SIGKILL)
- Preview server returns 500 — no dist output found
- `pnpm dev` starts Vite but it crashes during dep optimization

## Setup

```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
free -h
# Should show: Swap: 2.0Gi
```

## Safe Size

2GB is the sweet spot for a 1.8GB RAM VPS:
- Roughly 1:1 ratio with physical RAM
- Enough for esbuild spikes without thrashing
- Won't cause excessive disk I/O during normal operation

## Additional Mitigations

```bash
# Always prefix Node commands with heap limit
NODE_OPTIONS="--max-old-space-size=800" npx vite dev ...

# First-time setup: build creates dep cache, then dev reuses it
pnpm build   # one-time
pnpm dev     # subsequent — uses cached deps
```

## Removal

```bash
sudo swapoff /swapfile
# Remove line from /etc/fstab
sudo rm /swapfile
```
