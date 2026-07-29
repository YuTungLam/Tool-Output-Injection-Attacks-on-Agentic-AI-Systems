"""Small deterministic helpers shared by the harness."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize a value in a stable form suitable for hashing and comparison."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:
    """Return the hexadecimal SHA-256 digest of UTF-8 text."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_identifier(prefix: str, *parts: object, length: int = 16) -> str:
    """Build a readable deterministic identifier from canonical string parts."""

    material = "\x1f".join(str(part) for part in parts)
    return f"{prefix}-{sha256_text(material)[:length]}"
