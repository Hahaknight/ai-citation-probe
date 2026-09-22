"""Provider adapter contract.

Adapters must translate a provider response into an observation. They must not
consume raw keys from project files or synthesize citations from prose.
"""

from __future__ import annotations

import abc
from typing import Any

from ..models import ProviderObservation, ProviderProfile


class CitationProvider(abc.ABC):
    profile: ProviderProfile

    @abc.abstractmethod
    def run(
        self,
        *,
        probe_id: str,
        rendered_probe: str,
        sample_index: int,
        temperature: float,
    ) -> ProviderObservation:
        """Execute one probe sample and return normalized evidence."""

    @abc.abstractmethod
    def run_with_response(
        self,
        *,
        probe_id: str,
        rendered_probe: str,
        sample_index: int,
        temperature: float,
    ) -> tuple[ProviderObservation, Any]:
        """Execute and retain the provider's raw response for evidence."""
