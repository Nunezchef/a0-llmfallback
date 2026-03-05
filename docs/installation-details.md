# Installation Details

This repository is a self-contained plugin source.

## Distribution Model

- `plugin.yaml` at repository root is used by the Agent Zero plugin index.
- Runtime payload is included directly in this repository under `runtime/`.
- No `curl | bash` installer is required by this project.

## Runtime Files

- `runtime/usr/extensions/agent_init/_20_llm_fallback.py`
- `runtime/usr/helpers/llm_fallback.py`
- `runtime/webui/components/settings/agent/llm_fallback.html`

## Operational Notes

- This repository intentionally avoids runtime cloning and host patch scripts.
- Plugin loading behavior is expected to be handled by Agent Zero plugin infrastructure.
