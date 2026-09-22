"""Google Gemini grounding adapter placeholder."""

from __future__ import annotations

from ..models import (
    ProviderObservation,
    ProviderProfile,
    SearchMode,
    SurfaceEquivalence,
)
from .base import CitationProvider


class GeminiGroundingProvider(CitationProvider):
    def __init__(self, *, model: str) -> None:
        self.profile = ProviderProfile(
            id="gemini-grounding",
            model=model,
            search_mode=SearchMode.WEB_GROUNDING,
            surface_equivalence=SurfaceEquivalence.PARTIAL,
            supports_citations=True,
            notes="Grounding metadata must be retained as evidence.",
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
