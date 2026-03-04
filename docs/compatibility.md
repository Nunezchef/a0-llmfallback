# Compatibility

`a0-llmfallback` currently targets the standard Agent Zero repository layout and assumes these files exist:

- `run_ui.py`
- `python/helpers/settings.py`
- `webui/components/settings/agent/agent-settings.html`
- `usr/extensions/`
- `usr/helpers/`

The installer verifies the target looks like Agent Zero and then checks for expected anchor text before modifying core files. If those anchors are missing, the install aborts instead of guessing.

Current compatibility assumptions:

- A Git checkout of Agent Zero
- Python 3 available on the host
- `curl` or `wget` available for the one-line installer

Higher risk cases:

- heavily customized `python/helpers/settings.py`
- heavily customized `agent-settings.html`
- local edits that already added another settings section using the same anchors

If the installer aborts, use [manual-install.md](manual-install.md) to inspect the expected changes.
