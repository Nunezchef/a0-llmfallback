detect_a0_root() {
  if [ -n "${A0_ROOT:-}" ] && [ -d "${A0_ROOT}" ]; then
    printf '%s\n' "${A0_ROOT}"
    return 0
  fi

  if [ -d /a0 ]; then
    printf '/a0\n'
    return 0
  fi

  local cwd
  cwd="$(pwd)"
  if [ -f "${cwd}/run_ui.py" ] && [ -d "${cwd}/python" ] && [ -d "${cwd}/webui" ]; then
    printf '%s\n' "${cwd}"
    return 0
  fi

  return 1
}
