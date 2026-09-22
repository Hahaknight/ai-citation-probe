"""Immutable run manifest construction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .canonical import sha256_canonical
from .models import RunManifest
from .probe_set import ProbeSet


MANIFEST_SCHEMA = "run-manifest/0.1"


def provider_profile_hash(providers: list[dict[str, Any]]) -> str:
    return sha256_canonical(providers)


def build_manifest(
    *,
    run_id: str,
    probe_set: ProbeSet,
    providers: list[dict[str, Any]],
    notes: dict[str, Any] | None = None,
) -> RunManifest:
    return RunManifest(
        schema=MANIFEST_SCHEMA,
        run_id=run_id,
        created_at=datetime.now(timezone.utc),
        probe_set_version=probe_set.version,
        probe_set_hash=probe_set.computed_hash,
        providers=(),
        samples_per_probe=int(probe_set.defaults["samples_per_run"]),
        temperature=float(probe_set.defaults["temperature"]),
        provider_profile_hash=provider_profile_hash(providers),
        notes=notes or {},
    )
