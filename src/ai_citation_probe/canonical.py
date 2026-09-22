"""Canonical serialization used by manifest and probe-set hashes."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize deterministically as bare JSON.

    No trailing newline is added: the serialized bytes are the hash input.
    """

    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_probe_set(parsed_probe_set: dict[str, Any]) -> str:
    """Hash the parsed probe-set structure, not YAML bytes.

    The ``meta.canonical_hash`` field is removed before hashing. YAML comments,
    quoting, indentation, and line endings therefore cannot change the value.
    """

    normalized = {**parsed_probe_set}
    meta = {**normalized.get("meta", {})}
    meta.pop("canonical_hash", None)
    normalized["meta"] = meta
    return sha256_canonical(normalized)
