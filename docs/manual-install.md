# Manual Install

If you do not want to use `curl | bash`, clone the repo and run:

```bash
git clone https://github.com/Nunezchef/a0-llmfallback.git
cd a0-llmfallback
bash install.sh
```

Optional:

```bash
A0_ROOT=/path/to/agent-zero bash install.sh
```

Manual inspection points:

- review `install.sh`
- review `scripts/*.sh`
- review `runtime/`
- review [installation-details.md](installation-details.md)

After install, fully restart Agent Zero.
