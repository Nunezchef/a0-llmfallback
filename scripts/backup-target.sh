backup_target() {
  local root="$1"
  local stamp
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  local backup_root="${root}/.a0-llmfallback/backups/${stamp}"

  mkdir -p "${backup_root}/python/helpers"
  mkdir -p "${backup_root}/webui/components/settings/agent"
  mkdir -p "${backup_root}/usr/extensions/agent_init"
  mkdir -p "${backup_root}/usr/helpers"

  for rel in \
    "python/helpers/settings.py" \
    "webui/components/settings/agent/agent-settings.html" \
    "usr/extensions/agent_init/_20_llm_fallback.py" \
    "usr/helpers/llm_fallback.py" \
    "webui/components/settings/agent/llm_fallback.html"
  do
    if [ -f "${root}/${rel}" ]; then
      cp "${root}/${rel}" "${backup_root}/${rel}"
    fi
  done

  mkdir -p "${root}/.a0-llmfallback"
  printf '%s\n' "${stamp}" > "${root}/.a0-llmfallback/current"
  printf '%s\n' "${stamp}"
}
