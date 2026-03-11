# Shell tooling (macOS + homelab)

This is a curated install list matching your aliases/functions in `~/.zshrc`.

## Homebrew formulae

```bash
brew install \
  bat eza fd fzf ripgrep ripgrep-all jq yq jless \
  zoxide direnv atuin \
  dust htop bottom procs hyperfine tokei \
  xh doggo \
  gnu-sed coreutils \
  docker-compose \
  k9s kubectx stern minikube
```

## Optional / situational

```bash
brew install dive lazydocker aws-vault
```

## Notes
- `fzf` + `fd` + `bat` + `eza`: power most of your completion/preview UX.
- `ripgrep-all` (`rga`): required for your `lf='rga-fzf'` alias.
- `atuin`: better history search; plays nicely with `share_history` setups.
- `aws-vault`: a safer long-term home for AWS credentials than exporting them globally.

