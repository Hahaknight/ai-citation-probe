"""Anthropic adapter placeholder.

The MVP does not assume web search is available. If a search tool is enabled
later, profile metadata and evidence extraction must be updated together.
"""

from __future__ import annotations

from ..models import (
    ProviderObservation,
    ProviderProfile,
    SearchMode,
    SurfaceEquivalence,
)
from .base import CitationProvider


class AnthropicProvider(CitationProvider):
    def __init__(self, *, model: str, search_enabled: bool = False) -> None:
        self.profile = ProviderProfile(
            id="anthropic",
            model=model,
            search_mode=(
                SearchMode.WEB_GROUNDING if search_enabled else SearchMode.NONE
            ),
            surface_equivalence=(
                SurfaceEquivalence.PARTIAL
                if search_enabled
                else SurfaceEquivalence.NO
            ),
            supports_citations=search_enabled,
            notes="Search support must be explicit in the provider profile.",
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
