from __future__ import annotations

import hmac
import hashlib
from typing import Union


def sign_request(body: Union[str, bytes], secret_key: str) -> str:
    """Calculate HMAC SHA256 signature for a webhook body using the secret key.

    Mirrors the calculation flow from the API docs.
    """
    if isinstance(body, str):
        body_bytes = body.encode("utf-8")
    else:
        body_bytes = body

    return hmac.new(secret_key.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()


def verify_signature(body: Union[str, bytes], secret_key: str, signature: str) -> bool:
    """Verify the provided signature against the body using the secret key."""
    expected = sign_request(body, secret_key)
    # Use compare_digest to avoid timing attacks
    return hmac.compare_digest(expected, signature)


