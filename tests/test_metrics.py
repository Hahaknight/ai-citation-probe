from ai_citation_probe.metrics import (
    agreement_rate,
    jaccard,
    jaccard_intersect,
    jaccard_union,
)
import unittest


class MetricTests(unittest.TestCase):
    def test_agreement_rate_excludes_not_comparable(self):
        self.assertEqual(agreement_rate([True, True, None, False]), 2 / 3)
        self.assertIsNone(agreement_rate([None, None]))


    def test_jaccard_excludes_citationless_observations(self):
        self.assertEqual(jaccard([{"a.com"}, {"a.com", "b.com"}, None]), 0.5)
        self.assertIsNone(jaccard([None, set()]))

    def test_cross_provider_jaccard_reports_both_semantics(self):
        provider_a = [{"a.com", "b.com"}, None]
        provider_b = [None, {"a.com", "b.com"}]
        self.assertEqual(jaccard_union(provider_a, provider_b), 1.0)
        self.assertIsNone(jaccard_intersect(provider_a, provider_b))

        provider_a = [{"a.com"}, {"a.com", "b.com"}]
        provider_b = [{"a.com"}, {"a.com", "c.com"}]
        self.assertEqual(jaccard_union(provider_a, provider_b), 1 / 3)
        self.assertEqual(jaccard_intersect(provider_a, provider_b), 2 / 3)


if __name__ == "__main__":
    unittest.main()
