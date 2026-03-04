# Installation Details

## What `install.sh` does

1. Detects the Agent Zero root automatically or uses `A0_ROOT`
2. Downloads the repo tarball when run via `curl | bash`
3. Verifies the target looks like a valid Agent Zero checkout
4. Creates timestamped backups under `.a0-llmfallback/backups/`
5. Copies the runtime payload into `usr/` and `webui/components/settings/agent/`
6. Applies targeted, anchor-based edits to:
   - `python/helpers/settings.py`
   - `webui/components/settings/agent/agent-settings.html`
7. Writes install metadata for uninstall
8. Prints a full restart notice

## What `uninstall.sh` does

1. Detects the Agent Zero root automatically or uses `A0_ROOT`
2. Reads the most recent install metadata
3. Restores backed-up files when originals existed
4. Removes plugin-owned files that were newly added
5. Deletes the current install marker

## Agent Zero files added

- `usr/extensions/agent_init/_20_llm_fallback.py`
- `usr/helpers/llm_fallback.py`
- `webui/components/settings/agent/llm_fallback.html`

## Agent Zero files modified

- `python/helpers/settings.py`
- `webui/components/settings/agent/agent-settings.html`

## Trust notes

- The installer is intentionally small and readable.
- It fails closed if the expected anchors are missing.
- It creates exact file backups before modifications.
- It does not use `git reset`, `git checkout`, or destructive repo commands.
