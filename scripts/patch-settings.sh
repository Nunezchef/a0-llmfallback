patch_settings() {
  local root="$1"
  local _stamp="$2"
  local settings_file="${root}/python/helpers/settings.py"
  local agent_settings_file="${root}/webui/components/settings/agent/agent-settings.html"

  python3 - <<'PY' "${settings_file}" "${agent_settings_file}"
from pathlib import Path
import sys

settings_path = Path(sys.argv[1])
agent_settings_path = Path(sys.argv[2])

settings = settings_path.read_text()
agent_settings = agent_settings_path.read_text()

typed_anchor = "    browser_http_headers: dict[str, Any]\n"
typed_insert = typed_anchor + "    llm_fallback: dict[str, Any]\n"

defaults_anchor = '        browser_http_headers=get_default_value("browser_http_headers", {}),\n'
defaults_insert = defaults_anchor + '        llm_fallback=get_default_value("llm_fallback", _get_default_llm_fallback()),\n'

helper_anchor = "\ndef _get_api_key_field(settings: Settings, provider: str, title: str) -> SettingsField:\n"
helper_block = """
def _get_default_llm_fallback() -> dict[str, Any]:
    return {
        "enabled": False,
        "auto_recover": True,
        "recovery_check_interval_seconds": 300,
        "fail_on_http_statuses": [408, 429, 500, 502, 503, 504],
        "fail_on_error_substrings": [
            "insufficient_quota",
            "quota exceeded",
            "out of credits",
            "out of tokens",
            "rate limit",
            "resource exhausted",
            "context deadline exceeded",
        ],
        "roles": {
            role: {
                "enabled": False,
                "provider": "",
                "model": "",
                "api_base": "",
                "kwargs": {},
            }
            for role in ("chat", "utility", "browser", "embedding")
        },
    }


def _convert_llm_fallback_out(value: Any) -> dict[str, Any]:
    base = _get_default_llm_fallback()
    if isinstance(value, dict):
        base.update({k: v for k, v in value.items() if k != "roles"})
        roles = value.get("roles", {})
        if isinstance(roles, dict):
            for role_name, role_config in roles.items():
                if role_name not in base["roles"] or not isinstance(role_config, dict):
                    continue
                merged_role = dict(base["roles"][role_name])
                merged_role.update(role_config)
                if isinstance(merged_role.get("kwargs"), dict):
                    merged_role["kwargs"] = _dict_to_env(merged_role["kwargs"])
                base["roles"][role_name] = merged_role
    return base


def _convert_llm_fallback_in(value: Any) -> dict[str, Any]:
    base = _get_default_llm_fallback()
    if isinstance(value, dict):
        base.update({k: v for k, v in value.items() if k != "roles"})
        roles = value.get("roles", {})
        if isinstance(roles, dict):
            for role_name, role_config in roles.items():
                if role_name not in base["roles"] or not isinstance(role_config, dict):
                    continue
                merged_role = dict(base["roles"][role_name])
                merged_role.update(role_config)
                if isinstance(merged_role.get("kwargs"), str):
                    merged_role["kwargs"] = _env_to_dict(merged_role["kwargs"])
                elif not isinstance(merged_role.get("kwargs"), dict):
                    merged_role["kwargs"] = {}
                base["roles"][role_name] = merged_role
    return base
"""

convert_out_anchor = "    # normalize certain fields\n"
convert_out_insert = (
    '    out["settings"]["llm_fallback"] = _convert_llm_fallback_out(\n'
    '        out["settings"].get("llm_fallback")\n'
    '    )\n\n'
    + convert_out_anchor
)

convert_in_anchor = "        current[key] = value\n"
convert_in_insert = (
    '        if key == "llm_fallback":\n'
    '            current[key] = _convert_llm_fallback_in(value)\n'
    '            continue\n\n'
    + convert_in_anchor
)

if "llm_fallback: dict[str, Any]" not in settings:
    if typed_anchor not in settings:
        raise SystemExit("Missing typed settings anchor in python/helpers/settings.py")
    settings = settings.replace(typed_anchor, typed_insert, 1)

if "_get_default_llm_fallback" not in settings:
    if helper_anchor not in settings:
        raise SystemExit("Missing helper insertion anchor in python/helpers/settings.py")
    settings = settings.replace(helper_anchor, "\n" + helper_block + helper_anchor, 1)

if 'llm_fallback=get_default_value("llm_fallback", _get_default_llm_fallback())' not in settings:
    if defaults_anchor not in settings:
        raise SystemExit("Missing defaults anchor in python/helpers/settings.py")
    settings = settings.replace(defaults_anchor, defaults_insert, 1)

if '_convert_llm_fallback_out(' not in settings:
    if convert_out_anchor not in settings:
        raise SystemExit("Missing convert_out anchor in python/helpers/settings.py")
    settings = settings.replace(convert_out_anchor, convert_out_insert, 1)

if 'if key == "llm_fallback":' not in settings:
    if convert_in_anchor not in settings:
        raise SystemExit("Missing convert_in anchor in python/helpers/settings.py")
    settings = settings.replace(convert_in_anchor, convert_in_insert, 1)

nav_anchor = """              <li>
                <a href="#section-memory">
"""
nav_insert = """              <li>
                <a href="#section-llm-fallback">
                  <img src="/public/chat_model.svg" alt="LLM Fallback" />
                  <span>LLM Fallback</span>
                </a>
              </li>
""" + nav_anchor

section_anchor = """          <div id="section-memory" class="section">
"""
section_insert = """          <div id="section-llm-fallback" class="section">
            <x-component path="settings/agent/llm_fallback.html"></x-component>
          </div>

""" + section_anchor

if 'href="#section-llm-fallback"' not in agent_settings:
    if nav_anchor not in agent_settings:
        raise SystemExit("Missing navigation anchor in agent-settings.html")
    agent_settings = agent_settings.replace(nav_anchor, nav_insert, 1)

if 'path="settings/agent/llm_fallback.html"' not in agent_settings:
    if section_anchor not in agent_settings:
        raise SystemExit("Missing section anchor in agent-settings.html")
    agent_settings = agent_settings.replace(section_anchor, section_insert, 1)

settings_path.write_text(settings)
agent_settings_path.write_text(agent_settings)
PY
}
