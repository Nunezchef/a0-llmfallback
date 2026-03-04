#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[a0-llmfallback] %s\n' "$*"
}

die() {
  printf '[a0-llmfallback] ERROR: %s\n' "$*" >&2
  exit 1
}

detect_a0_root() {
  if [ -n "${A0_ROOT:-}" ] && [ -d "${A0_ROOT}" ]; then
    printf '%s\n' "${A0_ROOT}"
    return 0
  fi
  if [ -d /a0 ]; then
    printf '/a0\n'
    return 0
  fi
  return 1
}

restore_file() {
  local root="$1" backup_root="$2" rel="$3"
  local src="${backup_root}/${rel}"
  local dst="${root}/${rel}"
  if [ -f "${src}" ]; then
    mkdir -p "$(dirname "${dst}")"
    cp "${src}" "${dst}"
  else
    rm -f "${dst}"
  fi
}

main() {
  local root
  root="$(detect_a0_root)" || die "Unable to detect Agent Zero. Set A0_ROOT=/path/to/agent-zero and retry."

  local state_dir="${root}/.a0-llmfallback"
  local current_file="${state_dir}/current"
  [ -f "${current_file}" ] || die "No install marker found at ${current_file}"

  local stamp
  stamp="$(cat "${current_file}")"
  local backup_root="${state_dir}/backups/${stamp}"
  [ -d "${backup_root}" ] || die "Backup directory missing: ${backup_root}"

  restore_file "${root}" "${backup_root}" "python/helpers/settings.py"
  restore_file "${root}" "${backup_root}" "webui/components/settings/agent/agent-settings.html"
  restore_file "${root}" "${backup_root}" "usr/extensions/agent_init/_20_llm_fallback.py"
  restore_file "${root}" "${backup_root}" "usr/helpers/llm_fallback.py"
  restore_file "${root}" "${backup_root}" "webui/components/settings/agent/llm_fallback.html"

  rm -f "${current_file}"
  log "Uninstalled successfully from ${root}"
  printf '\n'
  printf 'HARD RESTART REQUIRED\n'
  printf 'Fully restart the Agent Zero backend now. A browser refresh alone is not enough.\n'
}

main "$@"
