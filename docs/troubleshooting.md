# Troubleshooting

## Installer says it cannot find Agent Zero

Set `A0_ROOT` explicitly:

```bash
A0_ROOT=/a0 bash install.sh
```

## Installer aborts on compatibility checks

Your local Agent Zero files likely differ from the expected anchors. Review:

- `python/helpers/settings.py`
- `webui/components/settings/agent/agent-settings.html`

Then compare against the behavior described in [installation-details.md](installation-details.md).

## Settings UI does not appear

- fully restart Agent Zero
- open a fresh settings session
- verify the file exists:
  - `webui/components/settings/agent/llm_fallback.html`

## Fallback does not trigger

Fallback only triggers on configured failures, such as:

- rate limits
- quota exhaustion
- transport failures
- matching configured error substrings

A plain `404 model not found` is not a default fallback trigger unless you add a matching substring.
