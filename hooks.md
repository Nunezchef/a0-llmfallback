# Runtime Hooks

This plugin keeps its runtime payload inside the repository:

- `runtime/usr/extensions/agent_init/_20_llm_fallback.py`
- `runtime/usr/helpers/llm_fallback.py`
- `runtime/webui/components/settings/agent/llm_fallback.html`

The `agent_init` extension installs model getter hooks that provide per-role failover behavior.
