import re

SECRET_REPLACEMENT = "<redacted>"

_QUERY_SECRET_RE = re.compile(r"(?i)([?&](?:access_token|token|key|pushkey)=)[^&\s)]+")
_PATH_SECRET_PATTERNS = (
    re.compile(r"(?i)(api\.day\.app/)[^/?\s)]+"),
    re.compile(r"(?i)(/v1/sender/)[^/?\s)]+"),
    re.compile(r"(?i)(/open-apis/bot/v2/hook/)[^/?\s)]+"),
    re.compile(r"(?i)(ntfy\.sh/)[^/?\s)]+"),
)
_SINGLE_SEGMENT_URL_RE = re.compile(
    r"(?i)(?P<prefix>https?://[^/?#\s)]+/)(?P<segment>[^/?#\s)]+)(?=(?:[?#\s)]|$))"
)
_SENSITIVE_SEGMENT_RE = re.compile(
    r"(?i)(?:^|[-_.])(?:token|secret|pushkey|topic|api[-_.]?key|access[-_.]?key|key)(?:$|[-_.]|\d)"
)


def redact_text(value: str) -> str:
    """Redact common notification provider secrets from text."""
    redacted = _QUERY_SECRET_RE.sub(rf"\1{SECRET_REPLACEMENT}", value)
    for pattern in _PATH_SECRET_PATTERNS:
        redacted = pattern.sub(rf"\1{SECRET_REPLACEMENT}", redacted)
    redacted = _SINGLE_SEGMENT_URL_RE.sub(_redact_sensitive_single_segment_url, redacted)
    return redacted


def redact_exception_message(error: Exception) -> Exception:
    """Redact string args in an exception while preserving its type and attrs."""
    if not error.args:
        return error

    error.args = tuple(redact_text(arg) if isinstance(arg, str) else arg for arg in error.args)
    return error


def _redact_sensitive_single_segment_url(match: re.Match) -> str:
    segment = match.group("segment")
    if _looks_sensitive_path_segment(segment):
        return f"{match.group('prefix')}{SECRET_REPLACEMENT}"
    return match.group(0)


def _looks_sensitive_path_segment(segment: str) -> bool:
    if _SENSITIVE_SEGMENT_RE.search(segment):
        return True

    has_alpha = any(character.isalpha() for character in segment)
    has_digit = any(character.isdigit() for character in segment)
    return len(segment) >= 16 and has_alpha and has_digit
