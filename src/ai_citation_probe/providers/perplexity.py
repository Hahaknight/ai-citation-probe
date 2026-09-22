"""Perplexity adapter placeholder; sonar responses may include citations."""

from __future__ import annotations

from ..models import (
    ProviderObservation,
    ProviderProfile,
    SearchMode,
    SurfaceEquivalence,
)
from .base import CitationProvider


class PerplexityProvider(CitationProvider):
    def __init__(self, *, model: str) -> None:
        self.profile = ProviderProfile(
            id="perplexity-sonar",
            model=model,
            search_mode=SearchMode.NATIVE_SEARCH,
            surface_equivalence=SurfaceEquivalence.DIRECT,
            supports_citations=True,
            notes="Closest consumer-surface proxy in the MVP provider matrix.",
        )

    def run(
        self,
        *,
        probe_id: str,
        rendered_probe: str,
        sample_index: int,
        temperature: float,
    ) -> ProviderObservation:
        raise NotImplementedError("M1 provider transport")
