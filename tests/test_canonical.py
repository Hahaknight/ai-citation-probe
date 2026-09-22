from ai_citation_probe.canonical import sha256_canonical, sha256_probe_set
import unittest


class CanonicalTests(unittest.TestCase):
    def test_hash_is_key_order_independent(self):
        self.assertEqual(
            sha256_canonical({"a": 1, "b": 2}),
            sha256_canonical({"b": 2, "a": 1}),
        )

    def test_probe_set_hash_uses_parsed_structure_without_hash_field(self):
        parsed = {
            "meta": {"version": "0.1.1", "canonical_hash": "old"},
            "questions": [],
        }
        modified = {
            "meta": {"version": "0.1.1", "canonical_hash": "new"},
            "questions": [],
        }

        self.assertEqual(sha256_probe_set(parsed), sha256_probe_set(modified))

    def test_probe_set_hash_has_fixed_bare_json_anchor(self):
        parsed = {"meta": {"version": "0.1.1"}, "questions": []}

        self.assertEqual(
            sha256_probe_set(parsed),
            "121745ec591a6665c5aa3410904db6f9ffb158b92d4fff43636cb8e4d814e37d",
        )


if __name__ == "__main__":
    unittest.main()
