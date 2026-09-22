import unittest

from ai_citation_probe.providers.perplexity import PerplexityProvider


class PerplexityTests(unittest.TestCase):
    def test_transport_response_becomes_observation(self):
        provider = PerplexityProvider(model="sonar")
        provider.api_key_resolver = lambda name: "test-key"
        raw = {
            "choices": [{"message": {"content": "Example is a brand."}}],
            "citations": ["https://example.com", "https://example.com"],
            "usage": {"total_tokens": 12, "cost": {"usd": 0.01}},
        }
        provider.transport = lambda *args: raw

        observation, response = provider.run_with_response(
            probe_id="q-1",
            rendered_probe="What is Example?",
            sample_index=0,
            temperature=0,
            brands=("Example",),
        )

        self.assertIs(response, raw)
        self.assertEqual(observation.status, "ok")
        self.assertEqual(len(observation.citations), 1)
        self.assertEqual(observation.token_usage, {"total_tokens": 12})
        self.assertEqual(observation.cost_usd, 0.01)

    def test_missing_api_key_fails_closed(self):
        provider = PerplexityProvider(model="sonar")
        provider.api_key_resolver = lambda name: None
        with self.assertRaises(RuntimeError):
            provider.run(
                probe_id="q-1",
                rendered_probe="x",
                sample_index=0,
                temperature=0,
                brands=("x",),
            )

    def test_evidence_category_uses_brand_text_and_citations(self):
        provider = PerplexityProvider(model="sonar")
        provider.api_key_resolver = lambda name: "test-key"
        citation = ["https://example.com"]

        cases = [
            ("Example text", True, "brand_with_citation"),
            ("Example text", False, "brand_mentioned"),
            ("Other text", True, "citation_only"),
            ("Other text", False, "not_cited"),
        ]
        for text, has_citations, expected in cases:
            provider.transport = lambda *args, text=text, has_citations=has_citations: {
                "choices": [{"message": {"content": text}}],
                "citations": citation if has_citations else [],
            }
            observation = provider.run(
                probe_id="q-1",
                rendered_probe="question",
                sample_index=0,
                temperature=0,
                brands=("Example",),
            )
            self.assertEqual(
                observation.evidence_category,
                expected,
            )
