install_runtime() {
  local repo_root="$1"
  local target_root="$2"
  local _stamp="$3"

  mkdir -p "${target_root}/usr/extensions/agent_init"
  mkdir -p "${target_root}/usr/helpers"
  mkdir -p "${target_root}/webui/components/settings/agent"

  cp "${repo_root}/runtime/usr/extensions/agent_init/_20_llm_fallback.py" "${target_root}/usr/extensions/agent_init/_20_llm_fallback.py"
  cp "${repo_root}/runtime/usr/helpers/llm_fallback.py" "${target_root}/usr/helpers/llm_fallback.py"
  cp "${repo_root}/runtime/webui/components/settings/agent/llm_fallback.html" "${target_root}/webui/components/settings/agent/llm_fallback.html"
}
