"""Loading and validation for the versioned probe-set protocol."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .canonical import sha256_probe_set


PROBE_SET_SCHEMA = "probe-set/0.1"
INTENTS = {"informational", "transactional", "navigational", "comparison"}
SURFACES = {"direct", "partial", "proxy", "no"}


class ProbeSetError(ValueError):
    """Raised when a probe-set does not satisfy the protocol."""


@dataclass(frozen=True)
class Probe:
    id: str
    text: str
    industry: str
    intent: str
    language: str
    region: str
    slots: tuple[str, ...]
    comparable_providers: tuple[str, ...]
    consumer_surface: str
    inclusion_reason: str
    added_in: str


@dataclass(frozen=True)
class ProbeSet:
    version: str
    declared_hash: str
    computed_hash: str
    defaults: dict[str, Any]
    probes: tuple[Probe, ...]

    @property
    def required_slots(self) -> set[str]:
        return {slot for probe in self.probes for slot in probe.slots}


def _require(mapping: dict[str, Any], key: str, context: str) -> Any:
    if key not in mapping or mapping[key] in (None, ""):
        raise ProbeSetError(f"{context}: missing required field '{key}'")
    return mapping[key]


def parse_probe_set(value: dict[str, Any]) -> ProbeSet:
    if not isinstance(value, dict):
        raise ProbeSetError("probe set must be a mapping")

    meta = value.get("meta")
    if not isinstance(meta, dict):
        raise ProbeSetError("meta must be a mapping")
    if meta.get("schema") != PROBE_SET_SCHEMA:
        raise ProbeSetError(f"meta.schema must be {PROBE_SET_SCHEMA!r}")
    version = _require(meta, "version", "meta")
    declared_hash = _require(meta, "canonical_hash", "meta")
    defaults = value.get("defaults")
    if not isinstance(defaults, dict):
        raise ProbeSetError("defaults must be a mapping")
    raw_questions = value.get("questions")
    if not isinstance(raw_questions, list) or not raw_questions:
        raise ProbeSetError("questions must be a non-empty list")

    probes: list[Probe] = []
    ids: set[str] = set()
    for index, raw in enumerate(raw_questions):
        context = f"questions[{index}]"
        if not isinstance(raw, dict):
            raise ProbeSetError(f"{context} must be a mapping")
        probe_id = _require(raw, "id", context)
        if probe_id in ids:
            raise ProbeSetError(f"{context}: duplicate id {probe_id!r}")
        ids.add(probe_id)
        intent = _require(raw, "intent", context)
        if intent not in INTENTS:
            raise ProbeSetError(f"{context}: unsupported intent {intent!r}")
        surface = _require(raw, "consumer_surface", context)
        if surface not in SURFACES:
            raise ProbeSetError(
                f"{context}: unsupported consumer_surface {surface!r}"
            )
        slots = raw.get("slots", [])
        comparable = raw.get("comparable_providers", [])
        if not isinstance(slots, list) or any(
            not isinstance(item, str) for item in slots
        ):
            raise ProbeSetError(f"{context}: slots must be a list of strings")
        if not isinstance(comparable, list) or any(
            not isinstance(item, str) for item in comparable
        ):
            raise ProbeSetError(
                f"{context}: comparable_providers must be a list of strings"
            )
        probes.append(
            Probe(
                id=probe_id,
                text=_require(raw, "text", context),
                industry=_require(raw, "industry", context),
                intent=intent,
                language=raw.get("language") or defaults.get("language"),
                region=raw.get("region") or defaults.get("region"),
                slots=tuple(slots),
                comparable_providers=tuple(comparable),
                consumer_surface=surface,
                inclusion_reason=_require(raw, "inclusion_reason", context),
                added_in=_require(raw, "added_in", context),
            )
        )

    return ProbeSet(
        version=version,
        declared_hash=declared_hash,
        computed_hash=sha256_probe_set(value),
        defaults=defaults,
        probes=tuple(probes),
    )


def load_probe_set(path: str | Path) -> ProbeSet:
    with Path(path).open("r", encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    probe_set = parse_probe_set(value)
    if probe_set.declared_hash != probe_set.computed_hash:
        raise ProbeSetError(
            "canonical_hash mismatch: "
            f"declared={probe_set.declared_hash}, computed={probe_set.computed_hash}"
        )
    return probe_set


def render_probe(probe: Probe, slots: dict[str, str]) -> str:
    missing = [slot for slot in probe.slots if slot not in slots]
    if missing:
        raise ProbeSetError(
            f"probe {probe.id}: missing slot values: {', '.join(missing)}"
        )
    return probe.text.format(**slots)
