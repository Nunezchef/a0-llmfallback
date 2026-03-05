# Compatibility

`a0-llmfallback` is distributed as a self-contained plugin repository.

Core assumptions:

- Agent Zero plugin loading supports plugin-owned runtime files
- The plugin source repository is reachable from the host installation path
- The host Agent Zero version supports `usr/extensions/agent_init`

Runtime files in this repository:

- `runtime/usr/extensions/agent_init/_20_llm_fallback.py`
- `runtime/usr/helpers/llm_fallback.py`
- `runtime/webui/components/settings/agent/llm_fallback.html`

Current limitation:

- If your host Agent Zero version does not yet support loading plugin-owned UI/runtime paths directly, this plugin may require host updates before full activation.
