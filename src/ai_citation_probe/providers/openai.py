"""OpenAI-compatible adapter placeholder.

M1 must decide whether search is enabled. A no-search profile is a model
capability measurement and must never be rendered as consumer AI-search
visibility.
"""

from __future__ import annotations

from ..models import (
    ProviderObservation,
    ProviderProfile,
    SearchMode,
    SurfaceEquivalence,
)
from .base import CitationProvider


class OpenAICompatibleProvider(CitationProvider):
    def __init__(
        self,
        *,
        model: str,
        search_enabled: bool,
        base_url: str | None = None,
    ) -> None:
        self.profile = ProviderProfile(
            id="openai-compatible",
            model=model,
            search_mode=(
                SearchMode.WEB_GROUNDING if search_enabled else SearchMode.NONE
            ),
            surface_equivalence=(
                SurfaceEquivalence.PARTIAL
                if search_enabled
                else SurfaceEquivalence.NO
            ),
            base_url=base_url,
            supports_citations=search_enabled,
            notes=(
                "Search-enabled profile requires explicit model/tool confirmation."
                if search_enabled
                else "No-search profile measures model capability only."
            ),
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
