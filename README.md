# A0 LLM Fallback

> Automatic per-role LLM failover for Agent Zero with fallback model settings, recovery behavior, and one-command installation.

[![Install](https://img.shields.io/badge/install-curl%20%7C%20bash-111827?style=for-the-badge)](https://github.com/Nunezchef/a0-llmfallback)
[![Target](https://img.shields.io/badge/target-Agent%20Zero-2563eb?style=for-the-badge)](https://github.com/frdel/agent-zero)
[![Mode](https://img.shields.io/badge/mode-LLM%20Failover-059669?style=for-the-badge)](https://github.com/Nunezchef/a0-llmfallback)

`a0-llmfallback` is a standalone add-on for Agent Zero, not a fork. It adds automatic failover for `chat`, `utility`, `browser`, and `embedding` model calls, so Agent Zero can retry against preconfigured fallback models when the primary provider fails or runs out of credits.

## What It Does

- Detects broad provider failures and quota-style errors
- Switches the affected role to a user-configured fallback model
- Retries the failed call once on the fallback model
- Tries the primary model again after the configured recovery interval
- Adds native settings UI inside Agent Zero for configuring fallback behavior

## Install

One-line install:

```bash
curl -fsSL https://raw.githubusercontent.com/Nunezchef/a0-llmfallback/main/install.sh | bash
```

Optional target:

```bash
curl -fsSL https://raw.githubusercontent.com/Nunezchef/a0-llmfallback/main/install.sh | A0_ROOT=/a0 bash
```

Marketplace path:

- This repo contains the canonical `plugin.yaml`.
- To appear in `agent0ai/a0-plugins`, add a lightweight index entry that points to this GitHub repo.

Review the exact file changes and installer behavior in [Installation Details](docs/installation-details.md) before running it.

## What Gets Changed In Agent Zero

Added:

- `usr/extensions/agent_init/_20_llm_fallback.py`
- `usr/helpers/llm_fallback.py`
- `webui/components/settings/agent/llm_fallback.html`

Modified:

- `python/helpers/settings.py`
- `webui/components/settings/agent/agent-settings.html`

The installer backs up each touched file before changing it.

## Compatibility

This add-on targets the current Agent Zero file layout with:

- `python/helpers/settings.py`
- `webui/components/settings/agent/agent-settings.html`
- `usr/` local extension support

Read [compatibility.md](docs/compatibility.md) before installing on a heavily customized checkout.

## Uninstall

If installed with `install.sh`, backups are stored under:

```bash
<agent-zero>/.a0-llmfallback/backups/<timestamp>/
```

To uninstall from a local clone:

```bash
bash uninstall.sh
```

## Trust And Transparency

- Short, auditable shell scripts
- Explicit backup and restore behavior
- Exact changed-files list
- Conservative compatibility checks
- Reversible uninstall

Full details: [Installation Details](docs/installation-details.md)

## Status

This is the initial standalone add-on scaffold. The runtime payload is real and copied from a working local implementation. The installer is designed to be safe-first and fail closed if the target Agent Zero tree does not match expected anchors.

## License

MIT. See [LICENSE](LICENSE).
