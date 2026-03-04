#!/usr/bin/env bash
set -euo pipefail

REPO_OWNER="${REPO_OWNER:-Nunezchef}"
REPO_NAME="${REPO_NAME:-a0-llmfallback}"
REPO_REF="${REPO_REF:-main}"
ARCHIVE_URL="https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/tar.gz/refs/heads/${REPO_REF}"

log() {
  printf '[a0-llmfallback] %s\n' "$*"
}

die() {
  printf '[a0-llmfallback] ERROR: %s\n' "$*" >&2
  exit 1
}

download_repo() {
  local tmp_dir archive
  tmp_dir="$(mktemp -d)"
  archive="${tmp_dir}/repo.tar.gz"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "${ARCHIVE_URL}" -o "${archive}" || die "Failed to download ${ARCHIVE_URL}"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "${archive}" "${ARCHIVE_URL}" || die "Failed to download ${ARCHIVE_URL}"
  else
    die "curl or wget is required"
  fi
  tar -xzf "${archive}" -C "${tmp_dir}" || die "Failed to unpack repo archive"
  printf '%s\n' "${tmp_dir}/${REPO_NAME}-${REPO_REF}"
}

main() {
  local repo_root cleanup_root
  cleanup_root=""

  if [ -f "${PWD}/scripts/detect-a0-root.sh" ] && [ -d "${PWD}/runtime" ]; then
    repo_root="${PWD}"
  else
    repo_root="$(download_repo)"
    cleanup_root="$(dirname "${repo_root}")"
  fi

  trap '[ -n "${cleanup_root}" ] && rm -rf "${cleanup_root}"' EXIT

  # shellcheck disable=SC1091
  . "${repo_root}/scripts/detect-a0-root.sh"
  # shellcheck disable=SC1091
  . "${repo_root}/scripts/verify-target.sh"
  # shellcheck disable=SC1091
  . "${repo_root}/scripts/backup-target.sh"
  # shellcheck disable=SC1091
  . "${repo_root}/scripts/install-runtime.sh"
  # shellcheck disable=SC1091
  . "${repo_root}/scripts/patch-settings.sh"

  local target_root
  target_root="$(detect_a0_root)" || die "Unable to detect Agent Zero. Set A0_ROOT=/path/to/agent-zero and retry."
  verify_target "${target_root}"
  local stamp
  stamp="$(backup_target "${target_root}")"
  install_runtime "${repo_root}" "${target_root}" "${stamp}"
  patch_settings "${target_root}" "${stamp}"

  log "Installed successfully into ${target_root}"
  printf '\n'
  printf 'HARD RESTART REQUIRED\n'
  printf 'Fully restart the Agent Zero backend now. A browser refresh alone is not enough.\n'
}

main "$@"
