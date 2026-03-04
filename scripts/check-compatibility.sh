check_compatibility() {
  local root="$1"
  local settings_file="${root}/python/helpers/settings.py"
  local agent_settings_file="${root}/webui/components/settings/agent/agent-settings.html"

  [ -x "$(command -v python3)" ] || die "python3 is required for the installer patch step"
  [ -f "${settings_file}" ] || die "Missing ${settings_file}"
  [ -f "${agent_settings_file}" ] || die "Missing ${agent_settings_file}"

  grep -q 'browser_http_headers: dict\[str, Any\]' "${settings_file}" \
    || die "Unsupported settings.py layout: typed anchor not found"
  grep -q 'browser_http_headers=get_default_value(\"browser_http_headers\", {})' "${settings_file}" \
    || die "Unsupported settings.py layout: default anchor not found"
  grep -q '^def _get_api_key_field(settings: Settings, provider: str, title: str) -> SettingsField:$' "${settings_file}" \
    || die "Unsupported settings.py layout: helper anchor not found"
  grep -q '^[[:space:]]*# normalize certain fields$' "${settings_file}" \
    || die "Unsupported settings.py layout: convert_out anchor not found"
  grep -q '^[[:space:]]*current\[key\] = value$' "${settings_file}" \
    || die "Unsupported settings.py layout: convert_in anchor not found"

  grep -q 'href=\"#section-memory\"' "${agent_settings_file}" \
    || die "Unsupported agent-settings.html layout: nav anchor not found"
  grep -q 'id=\"section-memory\" class=\"section\"' "${agent_settings_file}" \
    || die "Unsupported agent-settings.html layout: section anchor not found"
}
