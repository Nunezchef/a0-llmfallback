verify_target() {
  local root="$1"

  [ -d "${root}" ] || die "Target path does not exist: ${root}"
  [ -f "${root}/run_ui.py" ] || die "Missing ${root}/run_ui.py"
  [ -d "${root}/python" ] || die "Missing ${root}/python"
  [ -d "${root}/webui" ] || die "Missing ${root}/webui"
  [ -d "${root}/usr" ] || die "Missing ${root}/usr"

  if [ -d "${root}/.git" ]; then
    git -C "${root}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Target is not a usable git checkout"
  else
    die "Target must be a git checkout"
  fi
}
