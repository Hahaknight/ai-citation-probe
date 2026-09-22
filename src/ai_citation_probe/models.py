"""Core data contracts for run manifests and provider observations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal


class SearchMode(str, Enum):
    NONE = "none"
    NATIVE_SEARCH = "native_search"
    WEB_GROUNDING = "web_grounding"
    UNKNOWN = "unknown"


class SurfaceEquivalence(str, Enum):
    DIRECT = "direct"
    PARTIAL = "partial"
    PROXY = "proxy"
    NO = "no"


EvidenceCategory = Literal[
    "brand_mentioned",
    "brand_with_citation",
    "citation_only",
    "refused_or_unsearchable",
]


@dataclass(frozen=True)
class ProviderProfile:
    id: str
    model: str
    search_mode: SearchMode
    surface_equivalence: SurfaceEquivalence
    base_url: str | None = None
    supports_citations: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["search_mode"] = self.search_mode.value
        value["surface_equivalence"] = self.surface_equivalence.value
        return value


@dataclass(frozen=True)
class Citation:
    url: str
    title: str | None = None
    brand_hint: str | None = None


@dataclass(frozen=True)
class ProviderObservation:
    probe_id: str
    provider_id: str
    model: str
    sample_index: int
    status: Literal["ok", "refused", "error"]
    text_excerpt: str
    citations: tuple[Citation, ...] = ()
    evidence_category: EvidenceCategory | None = None
    cost_usd: float | None = None
    token_usage: dict[str, int] = field(default_factory=dict)
    latency_ms: int | None = None
    raw_response_uri: str | None = None


@dataclass(frozen=True)
class RunManifest:
    schema: Literal["run-manifest/0.1"]
    run_id: str
    created_at: datetime
    probe_set_version: str
    probe_set_hash: str
    providers: tuple[ProviderProfile, ...]
    samples_per_probe: int
    temperature: float
    provider_profile_hash: str
    notes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.samples_per_probe < 2:
            raise ValueError("samples_per_probe must be at least 2 for consistency")
        if not self.probe_set_version or not self.probe_set_hash:
            raise ValueError("probe-set version and canonical hash are both required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat(),
            "probe_set_version": self.probe_set_version,
            "probe_set_hash": self.probe_set_hash,
            "providers": [p.to_dict() for p in self.providers],
            "samples_per_probe": self.samples_per_probe,
            "temperature": self.temperature,
            "provider_profile_hash": self.provider_profile_hash,
            "notes": self.notes,
        }
