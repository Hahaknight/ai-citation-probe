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
            )
