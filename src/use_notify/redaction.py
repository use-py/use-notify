import re

SECRET_REPLACEMENT = "<redacted>"

_QUERY_SECRET_RE = re.compile(r"(?i)([?&](?:access_token|token|key|pushkey)=)[^&\s)]+")
_PATH_SECRET_PATTERNS = (
    re.compile(r"(?i)(api\.day\.app/)[^/?\s)]+"),
    re.compile(r"(?i)(/v1/sender/)[^/?\s)]+"),
    re.compile(r"(?i)(/open-apis/bot/v2/hook/)[^/?\s)]+"),
    re.compile(r"(?i)(ntfy\.sh/)[^/?\s)]+"),
)
_SINGLE_SEGMENT_URL_SECRET_RE = re.compile(r"(?i)(https?://[^/?#\s)]+/)[^/?#\s)]+(?=([?#\s)]|$))")


def redact_text(value: str) -> str:
    """Redact common notification provider secrets from text."""
    redacted = _QUERY_SECRET_RE.sub(rf"\1{SECRET_REPLACEMENT}", value)
    for pattern in _PATH_SECRET_PATTERNS:
        redacted = pattern.sub(rf"\1{SECRET_REPLACEMENT}", redacted)
    redacted = _SINGLE_SEGMENT_URL_SECRET_RE.sub(rf"\1{SECRET_REPLACEMENT}", redacted)
    return redacted


def redact_exception_message(error: Exception) -> Exception:
    """Redact string args in an exception while preserving its type and attrs."""
    if not error.args:
        return error

    error.args = tuple(redact_text(arg) if isinstance(arg, str) else arg for arg in error.args)
    return error
