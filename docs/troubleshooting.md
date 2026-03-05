# Troubleshooting

## Plugin does not appear in Agent Zero

- Verify `plugin.yaml` is present at repository root.
- Verify Agent Zero can reach this GitHub repository.

## Settings UI does not appear

- fully restart Agent Zero
- open a fresh settings session
- verify plugin runtime assets are available:
  - `runtime/webui/components/settings/agent/llm_fallback.html`

## Fallback does not trigger

Fallback only triggers on configured failures, such as:

- rate limits
- quota exhaustion
- transport failures
- matching configured error substrings

A plain `404 model not found` is not a default fallback trigger unless you add a matching substring.
