"""Perplexity transport with citation, usage, cost, and raw-response capture."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from ..models import (
    Citation,
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
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.transport: Callable[[str, str, str, dict[str, Any]], dict[str, Any]] = (
            self._urllib_post
        )
        self.api_key_resolver: Callable[[str], str | None] = os.environ.get

    @staticmethod
    def _urllib_post(
        url: str,
        api_key: str,
        payload_json: str,
        _context: dict[str, Any],
    ) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=payload_json.encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _extract_citations(payload: dict[str, Any]) -> tuple[Citation, ...]:
        citations: list[Citation] = []
        for item in payload.get("citations", []) or []:
            if isinstance(item, str):
                citations.append(Citation(url=item))
            elif isinstance(item, dict) and item.get("url"):
                citations.append(
                    Citation(url=item["url"], title=item.get("title"))
                )

        choices = payload.get("choices") or []
        message = choices[0].get("message", {}) if choices else {}
        for item in message.get("search_results", []) or []:
            if isinstance(item, str):
                citations.append(Citation(url=item))
            elif isinstance(item, dict) and item.get("url"):
                citations.append(
                    Citation(url=item["url"], title=item.get("title"))
                )

        unique: dict[str, Citation] = {}
        for citation in citations:
            unique.setdefault(citation.url, citation)
        return tuple(unique.values())

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        choices = payload.get("choices") or []
        if not choices:
            return ""
        return str(choices[0].get("message", {}).get("content", ""))

    @staticmethod
    def _extract_usage(payload: dict[str, Any]) -> tuple[dict[str, int], float | None]:
        usage = payload.get("usage") or {}
        token_keys = (
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "citation_tokens",
            "num_search_queries",
        )
        tokens = {
            key: int(usage[key])
            for key in token_keys
            if isinstance(usage.get(key), int)
        }
        cost_value = usage.get("cost")
        cost = (
            cost_value.get("usd")
            if isinstance(cost_value, dict)
            else cost_value
        )
        return tokens, (float(cost) if isinstance(cost, (int, float)) else None)

    def run(
        self,
        *,
        probe_id: str,
        rendered_probe: str,
        sample_index: int,
        temperature: float,
        brands: tuple[str, ...],
    ) -> ProviderObservation:
        observation, _ = self.run_with_response(
            probe_id=probe_id,
            rendered_probe=rendered_probe,
            sample_index=sample_index,
            temperature=temperature,
            brands=brands,
        )
        return observation

    def run_with_response(
        self,
        *,
        probe_id: str,
        rendered_probe: str,
        sample_index: int,
        temperature: float,
        brands: tuple[str, ...],
    ) -> tuple[ProviderObservation, dict[str, Any]]:
        api_key = self.api_key_resolver("PERPLEXITY_API_KEY")
        if not api_key:
            raise RuntimeError(
                "PERPLEXITY_API_KEY is required; keys are never stored"
            )
        payload = {
            "model": self.profile.model,
            "messages": [{"role": "user", "content": rendered_probe}],
            "temperature": temperature,
        }
        started = time.monotonic()
        try:
            response = self.transport(
                self.api_url,
                api_key,
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                {"probe_id": probe_id, "sample_index": sample_index},
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ) as error:
            # HTTPError covers API 4xx/5xx in this transport. M1 maps all
            # transport/API failures to refused_or_unsearchable; finer retry
            # classes are planned with live-smoke hardening.
            if isinstance(error, urllib.error.HTTPError):
                body = error.read().decode("utf-8", "replace")
                error_code = error.code
            else:
                body = str(error)
                error_code = type(error).__name__
            raw = {
                "error": error_code,
                "body": body,
                "probe_id": probe_id,
                "sample_index": sample_index,
            }
            return (
                ProviderObservation(
                    probe_id=probe_id,
                    provider_id=self.profile.id,
                    model=self.profile.model,
                    sample_index=sample_index,
                    status="error",
                    text_excerpt=body[:1000],
                    evidence_category="refused_or_unsearchable",
                    latency_ms=int((time.monotonic() - started) * 1000),
                ),
                raw,
            )

        latency = int((time.monotonic() - started) * 1000)
        citations = self._extract_citations(response)
        text = self._extract_text(response)
        tokens, cost = self._extract_usage(response)
        normalized_text = text.casefold()
        brand_mentioned = any(
            brand.casefold() in normalized_text for brand in brands if brand
        )
        if brand_mentioned and citations:
            category = "brand_with_citation"
        elif brand_mentioned:
            category = "brand_mentioned"
        elif citations:
            category = "citation_only"
        else:
            category = "not_cited"
        return (
            ProviderObservation(
                probe_id=probe_id,
                provider_id=self.profile.id,
                model=self.profile.model,
                sample_index=sample_index,
                status="ok",
                text_excerpt=text[:2000],
                citations=citations,
                evidence_category=category,
                cost_usd=cost,
                token_usage=tokens,
                latency_ms=latency,
            ),
            response,
        )
