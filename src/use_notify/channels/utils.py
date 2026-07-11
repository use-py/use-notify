import json
from typing import Dict, Iterable


class ProviderResponseError(RuntimeError):
    """Raised when a provider returns HTTP success with a failure payload."""

    def __init__(self, provider: str, field: str, value, detail: str):
        self.provider = provider
        self.field = field
        self.value = value
        self.detail = detail
        super().__init__(
            f"{provider} notification provider rejected response " f"({field}={value!r}): {detail}"
        )


def validate_business_response(
    response,
    provider: str,
    success_fields: Dict[str, Iterable],
) -> None:
    """Validate provider-specific success fields in a JSON response body."""
    try:
        payload = response.json()
    except (TypeError, ValueError):
        return

    if not isinstance(payload, dict):
        return

    for field, success_values in success_fields.items():
        if field not in payload:
            continue
        if payload[field] not in set(success_values):
            raise ProviderResponseError(
                provider=provider,
                field=field,
                value=payload[field],
                detail=_extract_error_detail(payload),
            )


def _extract_error_detail(payload: dict) -> str:
    for key in (
        "errmsg",
        "msg",
        "message",
        "error",
        "error_description",
        "desc",
        "errors",
    ):
        value = payload.get(key)
        if value:
            if isinstance(value, (list, tuple)):
                return ", ".join(str(item) for item in value)
            if isinstance(value, dict):
                return json.dumps(value, ensure_ascii=False, sort_keys=True)
            return str(value)

    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
