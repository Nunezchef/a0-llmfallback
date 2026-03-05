# Manual Integration (Development)

This repository no longer uses install/uninstall scripts.

For development or local debugging, inspect and integrate the plugin-owned runtime files:

- `runtime/usr/extensions/agent_init/_20_llm_fallback.py`
- `runtime/usr/helpers/llm_fallback.py`
- `runtime/webui/components/settings/agent/llm_fallback.html`

Use your Agent Zero environment's plugin workflow to load this repository as a plugin source.
