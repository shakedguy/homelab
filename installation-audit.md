# Installation Script Audit

**Date:** 2026-03-03  
**Compared:** `installation-script` vs actual system state  
**Status:** Resolved (script and dotfiles updated 2026-03-03)

---

## 1. Tools: Script vs Installed

### Homebrew formulae in script but NOT installed

| Formula       | Notes                                      |
|---------------|--------------------------------------------|
| `bottom`      | Not installed                              |
| `procs`       | Not installed                              |
| `hyperfine`   | Not installed                              |
| `coreutils`   | Not installed (macOS has BSD coreutils)   |
| `docker-compose` | Present at `/usr/local/bin/docker-compose` (likely Docker Desktop), not brew |
| `k9s`         | Not installed                              |
| `kubectx`     | Not installed                              |
| `stern`       | Not installed                              |
| `direnv`      | Not installed                              |
| `bun`         | Not via brew; installed via bun.sh         |
| `rust`        | Not via brew; installed via rustup        |

### Homebrew formulae installed but NOT in script

| Formula              | Notes                          |
|----------------------|--------------------------------|
| `lazysql`            | SQL client                     |
| `zsh-autocomplete`   | Zsh plugin (script has autosuggestions + syntax-highlighting only) |
| `go-task`            | Task runner                    |
| `glances`            | System monitor                |
| `mactop`             | macOS process monitor         |
| `nushell`            | Shell                         |
| `k6`                 | Load testing                   |
| `weasyprint`         | PDF from HTML                 |
| `docker-mac-net-connect` | Docker networking          |
| `dnsmasq`            | DNS/dhcp (likely dep)         |
| `duti`               | Default app handler           |
| `certifi`            | Python certs (likely dep)     |
| `tokei`              | In script and installed ✓    |

### Homebrew casks

| Script says | Installed |
|-------------|-----------|
| `numi`      | Not in brew casks; `numi-cli` at `/usr/local/bin/numi-cli` (from Numi app or other) |

**Installed casks:** android-platform-tools, font-jetbrains-mono-nerd-font, maccy, ngrok, redis-tui

---

## 2. Mise (not in script)

**mise is used** and activated in `~/.zshrc`:

```zsh
eval "$(~/.local/bin/mise activate zsh)"
```

**mise tools** (`~/.config/mise/config.toml`):

| Tool       | Version  |
|------------|----------|
| node       | 24       |
| pnpm       | 10.31    |
| python     | 3.14.2   |
| uv         | latest   |
| watchexec  | latest   |

- **uv** is installed via mise, not the script’s `curl | sh` installer.
- **python 3.14** is managed by mise; brew also has `python@3.14`.
- **watchexec** is not mentioned in the script.

---

## 3. .zshenv changes (actual vs script/template)

| Item                    | Actual ~/.zshenv                         | Script / dotfiles/zshenv.template      |
|-------------------------|------------------------------------------|----------------------------------------|
| Python path             | `/Library/Frameworks/.../3.13/bin` + `3.14` for UV_PYTHON | Template: 3.13 only |
| Google Cloud SDK        | `/Users/guyshaked/.google-cloud-sdk/bin` | Template: `$HOME/.google-cloud-sdk/bin` |
| GOOGLE_APPLICATION_CREDENTIALS | Commented out                    | Not in template                        |
| ANTHROPIC_*             | Commented out                            | In template (active)                    |
| HOMELAB_DIR             | Not set                                  | Added by script when deploying         |
| .duckdb in PATH         | Not present                              | In template                            |
| PNPM_HOME path_prepend  | Present ✓                                | Present ✓                              |

---

## 4. .zprofile (not in script)

`~/.zprofile` contains:

- Amazon Q pre block
- Python 3.14 PATH: `/Library/Frameworks/Python.framework/Versions/3.14/bin`

The script does not manage `.zprofile`.

---

## 5. .zshrc changes (actual vs dotfiles/zshrc)

| Item                    | Actual ~/.zshrc                           | dotfiles/zshrc                          |
|-------------------------|-------------------------------------------|----------------------------------------|
| mise activation         | `eval "$(~/.local/bin/mise activate zsh)"` | Missing                                |
| git-fzf path            | Hardcoded `/Users/guyshaked/.../git-fzf` | `${HOMELAB_DIR:-...}/scripts/git-fzf`  |
| homelab alias           | `zed ~/Desktop/dev/guy/homelab`           | `zed ${HOMELAB_DIR:-...}`              |
| redis-restart, mysql-restart, html2pdf | Hardcoded paths                  | `${HOMELAB_DIR:-...}`                  |
| Antigravity PATH        | At end of file                            | At end ✓                               |
| Duplicate kdpsd alias   | Present (lines 191–192)                    | Single alias ✓                         |

---

## 6. Summary: what to update in the script

1. **Add mise**
   - Install: `curl https://mise.run | sh` (or similar)
   - Add `eval "$(~/.local/bin/mise activate zsh)"` to dotfiles/zshrc
   - Optionally document mise tools (node, pnpm, python, uv, watchexec)

2. **Brew formulae**
   - Remove or mark optional: `bottom`, `procs`, `hyperfine`, `coreutils`, `k9s`, `kubectx`, `stern`, `direnv` if you don’t use them
   - Add: `lazysql`, `zsh-autocomplete`, `go-task`, `glances`, `mactop`, `nushell`, `k6`, `weasyprint` if you want them in the script

3. **uv**
   - Prefer mise for uv instead of the standalone installer when mise is used

4. **numi**
   - Document that `numi-cli` comes from Numi app (or another source), not brew cask `numi`

5. **Dotfiles**
   - Add mise activation to `dotfiles/zshrc`
   - Run `--sync-from-home` to refresh `dotfiles/zshrc` from current `~/.zshrc`

6. **.zprofile**
   - Add a step to create/update `.zprofile` if you want it managed by the script
