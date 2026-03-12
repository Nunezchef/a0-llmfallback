import inspect
import re
import time
from dataclasses import dataclass
from types import MethodType
from typing import Any, Callable


ROLE_ATTRS = {
    "chat": "chat_model",
    "utility": "utility_model",
    "browser": "browser_model",
    "embedding": "embeddings_model",
}

ROLE_GETTERS = {
    "chat": "get_chat_model",
    "utility": "get_utility_model",
    "browser": "get_browser_model",
    "embedding": "get_embedding_model",
}

_EVENT_COOLDOWN_SECONDS = 20
_LAST_EVENT_AT: dict[tuple[str, str], float] = {}

_TIMEOUT_MARKERS = (
    "timeout",
    "timed out",
    "deadline exceeded",
    "context deadline exceeded",
    "read timed out",
    "connection timed out",
)
_RATE_LIMIT_MARKERS = (
    "rate limit",
    "too many requests",
    "429",
    "weekly usage limit",
)
_QUOTA_MARKERS = (
    "insufficient_quota",
    "quota exceeded",
    "out of credits",
    "out of tokens",
    "resource exhausted",
)
_PROVIDER_MARKERS = (
    "service unavailable",
    "temporarily unavailable",
    "connection error",
    "connection reset",
    "provider error",
    "apiconnectionerror",
)


@dataclass
class RoleState:
    mode: str = "primary"
    failed_at: float = 0.0


_STATE = {role: RoleState() for role in ROLE_ATTRS}


def reset_state() -> None:
    for role in _STATE:
        _STATE[role] = RoleState()
    _LAST_EVENT_AT.clear()


def get_state(role: str) -> RoleState:
    return _STATE.setdefault(role, RoleState())


def _coerce_fallback_settings(value: Any) -> dict[str, Any]:
    data = value if isinstance(value, dict) else {}
    roles = data.get("roles", {}) if isinstance(data.get("roles", {}), dict) else {}
    return {
        "enabled": bool(data.get("enabled", False)),
        "auto_recover": bool(data.get("auto_recover", True)),
        "recovery_check_interval_seconds": int(
            data.get("recovery_check_interval_seconds", 300) or 300
        ),
        "fail_on_http_statuses": list(
            data.get("fail_on_http_statuses", [408, 429, 500, 502, 503, 504])
        ),
        "fail_on_error_substrings": list(
            data.get(
                "fail_on_error_substrings",
                [
                    "insufficient_quota",
                    "quota exceeded",
                    "out of credits",
                    "out of tokens",
                    "rate limit",
                    "resource exhausted",
                    "context deadline exceeded",
                    "timed out",
                    "timeout",
                    "connection error",
                ],
            )
        ),
        "roles": {
            role: {
                "enabled": bool((roles.get(role) or {}).get("enabled", False)),
                "provider": str((roles.get(role) or {}).get("provider", "") or ""),
                "model": str((roles.get(role) or {}).get("model", "") or ""),
                "api_base": str((roles.get(role) or {}).get("api_base", "") or ""),
                "kwargs": (
                    (roles.get(role) or {}).get("kwargs", {})
                    if isinstance((roles.get(role) or {}).get("kwargs", {}), dict)
                    else {}
                ),
            }
            for role in ROLE_ATTRS
        },
    }


def get_fallback_settings() -> dict[str, Any]:
    from python.helpers import settings as settings_helper

    current = settings_helper.get_settings()
    return _coerce_fallback_settings(current.get("llm_fallback", {}))


def is_role_enabled(role: str, config: dict[str, Any] | None = None) -> bool:
    cfg = config or get_fallback_settings()
    role_cfg = cfg["roles"].get(role, {})
    return bool(
        cfg.get("enabled")
        and role_cfg.get("enabled")
        and role_cfg.get("provider")
        and role_cfg.get("model")
    )


def mark_failed(role: str, failed_at: float | None = None) -> None:
    state = get_state(role)
    state.mode = "fallback"
    state.failed_at = failed_at if failed_at is not None else time.monotonic()


def mark_recovered(role: str) -> None:
    state = get_state(role)
    state.mode = "primary"
    state.failed_at = 0.0


def should_use_fallback(role: str, config: dict[str, Any] | None = None) -> bool:
    cfg = config or get_fallback_settings()
    state = get_state(role)
    if state.mode != "fallback":
        return False
    if not is_role_enabled(role, cfg):
        mark_recovered(role)
        return False
    if cfg.get("auto_recover", True):
        interval = int(cfg.get("recovery_check_interval_seconds", 300) or 300)
        if state.failed_at and (time.monotonic() - state.failed_at) >= interval:
            mark_recovered(role)
            return False
    return True


def _extract_error_text(exc: Exception) -> str:
    return " ".join(str(part) for part in getattr(exc, "args", ()) if part).strip() or str(exc)


def _extract_status_code(exc: Exception, text: str) -> int | None:
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int):
        return status_code
    match = re.search(r"statuscode\"\s*:\s*(\d+)", text, re.IGNORECASE)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def classify_failover_reason(exc: Exception, config: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = config or get_fallback_settings()
    raw_text = _extract_error_text(exc)
    text = raw_text.lower()
    status_code = _extract_status_code(exc, raw_text)

    if isinstance(status_code, int):
        if status_code == 429:
            reason = "rate_limit"
        elif status_code in (408, 504):
            reason = "timeout"
        elif status_code >= 500:
            reason = "provider_error"
        else:
            reason = "http_error"
        return {"reason": reason, "status_code": status_code, "error_text": raw_text}

    if any(marker in text for marker in _TIMEOUT_MARKERS):
        return {"reason": "timeout", "status_code": None, "error_text": raw_text}
    if any(marker in text for marker in _RATE_LIMIT_MARKERS):
        return {"reason": "rate_limit", "status_code": None, "error_text": raw_text}
    if any(marker in text for marker in _QUOTA_MARKERS):
        return {"reason": "quota_exhausted", "status_code": None, "error_text": raw_text}
    if any(marker in text for marker in _PROVIDER_MARKERS):
        return {"reason": "provider_error", "status_code": None, "error_text": raw_text}

    substrings = [
        str(item).strip().lower()
        for item in cfg.get("fail_on_error_substrings", [])
        if str(item).strip()
    ]
    if any(item in text for item in substrings):
        return {"reason": "configured_error_match", "status_code": None, "error_text": raw_text}

    return {"reason": "unknown_error", "status_code": None, "error_text": raw_text}


def should_failover(role: str, exc: Exception, config: dict[str, Any] | None = None) -> bool:
    cfg = config or get_fallback_settings()
    if not is_role_enabled(role, cfg):
        return False

    status_code = _extract_status_code(exc, _extract_error_text(exc))
    if isinstance(status_code, int):
        statuses = {
            int(code) for code in cfg.get("fail_on_http_statuses", []) if isinstance(code, int)
        }
        if status_code in statuses or status_code >= 500:
            return True

    reason_info = classify_failover_reason(exc, cfg)
    return reason_info["reason"] != "unknown_error"


def _normalize_kwargs(value: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(item, str):
            try:
                normalized[key] = int(item)
                continue
            except ValueError:
                try:
                    normalized[key] = float(item)
                    continue
                except ValueError:
                    pass
        normalized[key] = item
    return normalized


def _build_model_config(agent: Any, role: str, use_fallback: bool) -> Any:
    import models

    primary = getattr(agent.config, ROLE_ATTRS[role])
    if not use_fallback:
        return primary

    cfg = get_fallback_settings()
    role_cfg = cfg["roles"][role]
    if not is_role_enabled(role, cfg):
        return primary

    return models.ModelConfig(
        type=primary.type,
        provider=role_cfg["provider"],
        name=role_cfg["model"],
        api_base=role_cfg["api_base"],
        ctx_length=getattr(primary, "ctx_length", 0),
        limit_requests=getattr(primary, "limit_requests", 0),
        limit_input=getattr(primary, "limit_input", 0),
        limit_output=getattr(primary, "limit_output", 0),
        vision=getattr(primary, "vision", False),
        kwargs=_normalize_kwargs(role_cfg["kwargs"]),
    )


def build_model(agent: Any, role: str, use_fallback: bool = False) -> Any:
    import models

    config = _build_model_config(agent, role, use_fallback)
    kwargs = config.build_kwargs()
    if role in ("chat", "utility"):
        return models.get_chat_model(
            config.provider, config.name, model_config=config, **kwargs
        )
    if role == "browser":
        return models.get_browser_model(
            config.provider, config.name, model_config=config, **kwargs
        )
    return models.get_embedding_model(
        config.provider, config.name, model_config=config, **kwargs
    )


def _should_emit_observability_event(role: str, event: str) -> bool:
    now = time.monotonic()
    key = (role, event)
    last = _LAST_EVENT_AT.get(key, 0.0)
    if (now - last) < _EVENT_COOLDOWN_SECONDS:
        return False
    _LAST_EVENT_AT[key] = now
    return True


def _emit_observability_event(
    agent: Any,
    role: str,
    event: str,
    reason: str,
    error_text: str = "",
) -> None:
    if not _should_emit_observability_event(role, event):
        return

    try:
        from python.helpers.notification import (
            NotificationManager,
            NotificationPriority,
            NotificationType,
        )

        primary_cfg = getattr(agent.config, ROLE_ATTRS[role], None)
        fallback_cfg = get_fallback_settings()["roles"].get(role, {})
        fallback_target = f'{fallback_cfg.get("provider", "?")}/{fallback_cfg.get("model", "?")}'
        primary_target = "unknown"
        if primary_cfg is not None:
            primary_target = f"{getattr(primary_cfg, 'provider', '?')}/{getattr(primary_cfg, 'name', '?')}"

        if event == "activated":
            NotificationManager.send_notification(
                type=NotificationType.WARNING,
                priority=NotificationPriority.HIGH,
                title=f"LLM fallback activated ({role})",
                message=f"Switched to {fallback_target} due to {reason.replace('_', ' ')}.",
                detail=f"Primary: {primary_target}\nFallback: {fallback_target}\nReason: {reason}\nError: {error_text}",
                display_time=8,
                group=f"llm_fallback_{role}",
            )
        else:
            NotificationManager.send_notification(
                type=NotificationType.SUCCESS,
                priority=NotificationPriority.NORMAL,
                title=f"LLM primary recovered ({role})",
                message=f"Returned to {primary_target} after fallback period.",
                detail=f"Primary: {primary_target}\nPrevious fallback: {fallback_target}",
                display_time=6,
                group=f"llm_fallback_{role}",
            )
    except Exception:
        pass

    if role != "chat" or agent is None:
        return
    try:
        if event == "activated":
            agent.hist_add_warning(
                f"[LLM Fallback] Chat switched to fallback due to {reason.replace('_', ' ')}."
            )
        else:
            agent.hist_add_warning("[LLM Fallback] Chat primary model recovered.")
    except Exception:
        pass


class FallbackModelProxy:
    def __init__(self, agent: Any, role: str, builder: Callable[[bool], Any]):
        self._agent = agent
        self._role = role
        self._builder = builder
        self._primary_model: Any | None = None
        self._fallback_model: Any | None = None

    def _get_model(self, use_fallback: bool) -> Any:
        if use_fallback:
            if self._fallback_model is None:
                self._fallback_model = self._builder(True)
            return self._fallback_model
        if self._primary_model is None:
            self._primary_model = self._builder(False)
        return self._primary_model

    def _resolve_fallback_usage(self) -> bool:
        previous_mode = get_state(self._role).mode
        use_fallback = should_use_fallback(self._role)
        if previous_mode == "fallback" and get_state(self._role).mode == "primary":
            _emit_observability_event(
                agent=self._agent,
                role=self._role,
                event="recovered",
                reason="recovery_interval_elapsed",
            )
        return use_fallback

    def _call_with_retry(self, attr_name: str, *args: Any, **kwargs: Any) -> Any:
        use_fallback = self._resolve_fallback_usage()
        target = getattr(self._get_model(use_fallback), attr_name)
        try:
            result = target(*args, **kwargs)
        except Exception as exc:
            if use_fallback or not should_failover(self._role, exc):
                raise
            reason_info = classify_failover_reason(exc)
            mark_failed(self._role)
            _emit_observability_event(
                agent=self._agent,
                role=self._role,
                event="activated",
                reason=reason_info["reason"],
                error_text=reason_info["error_text"],
            )
            retry_target = getattr(self._get_model(True), attr_name)
            return retry_target(*args, **kwargs)

        if inspect.isawaitable(result):
            return self._await_result(attr_name, result, use_fallback, args, kwargs)
        return result

    async def _await_result(
        self,
        attr_name: str,
        result: Any,
        use_fallback: bool,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        try:
            return await result
        except Exception as exc:
            if use_fallback or not should_failover(self._role, exc):
                raise
            reason_info = classify_failover_reason(exc)
            mark_failed(self._role)
            _emit_observability_event(
                agent=self._agent,
                role=self._role,
                event="activated",
                reason=reason_info["reason"],
                error_text=reason_info["error_text"],
            )
            retry_target = getattr(self._get_model(True), attr_name)
            retry_result = retry_target(*args, **kwargs)
            if inspect.isawaitable(retry_result):
                return await retry_result
            return retry_result

    def __getattr__(self, attr_name: str) -> Any:
        current = getattr(self._get_model(False), attr_name)
        if not callable(current):
            return current

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return self._call_with_retry(attr_name, *args, **kwargs)

        return wrapped


def make_proxy(agent: Any, role: str) -> FallbackModelProxy:
    return FallbackModelProxy(
        agent=agent,
        role=role,
        builder=lambda use_fallback: build_model(agent, role, use_fallback),
    )


def install_agent_fallback_hooks(agent: Any) -> None:
    if getattr(agent, "_llm_fallback_hooks_installed", False):
        return

    for role, getter_name in ROLE_GETTERS.items():
        def _wrapped(self: Any, _role: str = role) -> FallbackModelProxy:
            return make_proxy(self, _role)

        setattr(agent, getter_name, MethodType(_wrapped, agent))

    agent._llm_fallback_hooks_installed = True
