from typing import Any
import json
import hashlib


def _deep_hash(obj: Any) -> str:
    """SHA-256 digest of anything serializable."""

    def _default(o):
        try:
            return o.model_dump()
        except AttributeError:
            return repr(o)

    return hashlib.sha256(
        json.dumps(obj, default=_default, sort_keys=True).encode()
    ).hexdigest()
