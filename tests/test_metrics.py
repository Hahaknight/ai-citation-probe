from ai_citation_probe.metrics import agreement_rate, jaccard
import unittest


class MetricTests(unittest.TestCase):
    def test_agreement_rate_excludes_not_comparable(self):
        self.assertEqual(agreement_rate([True, True, None, False]), 2 / 3)
        self.assertIsNone(agreement_rate([None, None]))


    def test_jaccard_excludes_citationless_observations(self):
        self.assertEqual(jaccard([{"a.com"}, {"a.com", "b.com"}, None]), 0.5)
        self.assertIsNone(jaccard([None, set()]))


if __name__ == "__main__":
    unittest.main()
